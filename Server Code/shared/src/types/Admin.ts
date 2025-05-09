import { Schema, model, Types } from 'mongoose';

export interface Admin {
    _id?: Types.ObjectId;
    name: string;
    email: string;
    password: string;
}
const adminSchema = new Schema<Admin>({
    name : {
        type : String,
        required : true
    },
    email : {
        type : String,
        required : true
    },
    password : {
        type : String,
        required : true
    },
})
const AdminM = model<Admin>('AdminM', adminSchema)
export default AdminM