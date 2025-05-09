import { Schema, model, Types} from 'mongoose';

export interface Item {
    name : string;
    unit_price : number;
    total_price : number;
    quantity : number;
}

export interface Client {
    _id?: Types.ObjectId;
    userName: string;
    email : string;
    password? :string;
    card_Id? : string;
    customer_Id?: string;
    entry_date?: Date;
    processing_date? : Date;
    box? : Item[];
    total_amount? : number;
    credit? : number;
}

const clientSchema = new Schema<Client>({
    userName: { 
        type: String,
        required: false  
    },
    email: {
        type: String,
        required: false
    },
    password : {
        type : String,
        required : false
    },
    card_Id: {  
        type: String,
        required: false
    },
    customer_Id: {  
        type: String,
        required: false,
        default : "none"
    },
    entry_date: {
        type: Date,
        required: false,
        default: Date.now
    },
    processing_date: {
        type: Date,
        required: false
    },
    box: [{  
        name: {
            type: String,
            required: false
        },
        unit_price: {
            type: Number,
            required: false
        },
        total_price: {
            type: Number,
            required: false
        },
        quantity: {
            type: Number,
            required: false
        }
    }],
    credit: {  
        type: Number,
        required: false,
        default : 500
    },
    total_amount: {
        type: Number,
        required: false
    }
});

const ClientM = model<Client>('ClientM', clientSchema)
export default ClientM