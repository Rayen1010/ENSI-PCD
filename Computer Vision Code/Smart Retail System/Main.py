from pymongo import MongoClient
from datetime import datetime
from bson.decimal128 import Decimal128
from decimal import Decimal, InvalidOperation
import os
from dotenv import load_dotenv
import certifi
import argparse
import time
import json
from tracking_and_identifying import ObjectTracker
from red_text_detector_with_Paddle_OCR import RedTextDetector
from OcrCorrecting import get_correct_words


# Load environment variables
load_dotenv()

class MongoDBHandler:
    """Enhanced MongoDB handler with purchase processing capabilities"""
    
    def __init__(self):
        self.client = None
        self.INITIAL_CREDIT = Decimal("500")
        
    def __enter__(self):
        self.client = self._get_client()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
    
    def _get_client(self):
        """Secure MongoDB connection with robust timeout settings"""
        connection_string = os.getenv("MONGODB_URI")
        if not connection_string:
            raise ValueError("MONGODB_URI not found in environment variables")

        try:
            client = MongoClient(
                connection_string,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000
            )
            client.admin.command('ping')
            return client
        except Exception as e:
            raise ConnectionError(f"MongoDB connection failed: {str(e)}")
    
    def _convert_to_decimal128(self, value):
        """Type-safe decimal conversion"""
        try:
            if isinstance(value, Decimal128):
                return value
            return Decimal128(str(Decimal(str(value))))
        except (InvalidOperation, TypeError, ValueError) as e:
            raise ValueError(f"Invalid decimal value: {value} - {str(e)}")
    
    def save_purchase_data(self, report_data):
        """
        Save complete purchase data from the analysis report
        """
        try:
            with self as db_handler:
                db = db_handler.client["customerspurchases"]
                collection = db["customer_purchases"]
                
                if not report_data.get('customers'):
                    print("⚠️ No customer data to save")
                    return False
                
                customer_data = report_data['customers'][0]
                metadata = report_data['metadata']
                
                # Process financial data with decimal precision
                try:
                    total_price = Decimal(str(customer_data['financial_summary']['total_price']))
                    remaining_credit = self.INITIAL_CREDIT - total_price
                    
                    if remaining_credit < 0:
                        print("⚠️ Purchase exceeds available credit")
                        return False
                    
                
                except (KeyError, InvalidOperation) as e:
                    raise ValueError(f"Invalid financial data: {str(e)}")
                
                # Prepare MongoDB document (without metadata)
                document = {
                    "customer_Id": customer_data['customer_id'],
                    "entry_date": datetime.now(),
                    "processing_date": metadata['processing_date'], 
                    "box": [],
                    "total_amount": self._convert_to_decimal128(total_price),
                    #"credit": self._convert_to_decimal128(remaining_credit)
                }
                
                # Add all purchased items
                for item_name, item_data in customer_data['purchased_items'].items():
                    document["box"].append({
                        "name": item_name,
                        "quantity": item_data['quantity'],
                        "unit_price": self._convert_to_decimal128(item_data['unit_price']),
                        "total_price": self._convert_to_decimal128(item_data['item_total'])
                    })
                
                print(document)
                ObjectTracker.send_customer_box_to_api(document)
                # Insert document
                #result = collection.insert_one(document)
                
                print(f"✅ Saved purchase for customer {customer_data['customer_id']}")
                return True
                
        except Exception as e:
            print(f"❌ Failed to save purchase data: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="Smart Store Analytics Pipeline with MongoDB Integration",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--input', type=str, default=r"Test Videos\besttest.mp4", 
                       help='Path to input video file')
    parser.add_argument('--output', type=str, default='Output Videos', 
                       help='Directory for output files')
    parser.add_argument('--skip-frames', type=int, default=3, 
                       help='Number of frames to skip during processing')
    parser.add_argument('--capture-interval', type=int, default=3, 
                       help='Interval in seconds between frame captures')
    parser.add_argument('--no-db', action='store_true',
                       help='Skip database saving if flag is present')
    args = parser.parse_args()

    try:
        start_time = time.time()
        print("\n🚀 Starting Smart Store Analytics Pipeline...")
        
        # Validate input
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Input file not found: {args.input}")

        # Initialize components
        tracker = ObjectTracker()
        tracker.video_path = args.input
        tracker.output_path = os.path.join(args.output, f"Tracking_Output_{time.strftime('%Y%m%d_%H%M%S')}.mp4")
        tracker.frame_skip = args.skip_frames
        tracker.capture_interval = args.capture_interval

        # Process video
        print("\n🎥 Processing video...")
        tracker.run()
        
        # Detect purchases
        print("\n🔍 Analyzing purchases...")
        purchased_items = get_correct_words()
        
        # Generate report
        report = generate_report(tracker, purchased_items, start_time)
        save_results(report, args.output)

        # MongoDB integration
        if not args.no_db and report.get('customers'):
            print("\n💾 Connecting to MongoDB...")
            db_handler = MongoDBHandler()
            if not db_handler.save_purchase_data(report):
                print("⚠️ Proceeding without database save")
        else:
            print("\nℹ️ Skipping database save as requested")

        print(f"\n✅ Pipeline completed in {time.time() - start_time:.2f} seconds")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        raise

def generate_report(tracker, purchased_items, start_time):
    """Generate comprehensive analytics report"""
    processing_time = time.time() - start_time
    
    report = {
        'metadata': {
            'processing_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'processing_time_seconds': round(processing_time, 2),
            'input_video': tracker.video_path,
            'output_video': tracker.output_path,
        },
        'statistics': {
            'total_customers': tracker.entry_counter,
            'total_frames_processed': tracker.frame_count,
            'processing_fps': round(tracker.frame_count/processing_time, 2),
        },
        'customers': [],
    }
    
    if tracker.entry_counter > 0 and purchased_items:
        customer_data = {
            'customer_id': tracker.entry_counter,  # Using entry count as ID
            'entry_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
            'purchased_items': {},
            'financial_summary': {
                'total_price': 0,  
                'item_count': 0
            }
        }
        
        # Calculate item totals
        for item, price in purchased_items.items():
            quantity = 1  # Default quantity
            item_total = quantity * price
            
            customer_data['purchased_items'][item] = {
                'quantity': quantity,
                'unit_price': price,
                'item_total': item_total
            }
            customer_data['financial_summary']['total_price'] += item_total 
            customer_data['financial_summary']['item_count'] += quantity
        
        report['customers'].append(customer_data)
    
    return report

def save_results(data, output_dir):
    """Save analytics report to JSON"""
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, 'analysis_report.json')
    
    try:
        with open(report_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"📄 Report saved to {report_path}")
    except IOError as e:
        print(f"⚠️ Failed to save report: {str(e)}")

if __name__ == "__main__":
    main()