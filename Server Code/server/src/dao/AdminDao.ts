import { Types } from 'mongoose';
import { Admin } from '../../../shared/src/types/Admin';

export interface AdminDao {
  createAdmin(admin : Admin) : Promise<Admin | undefined>;
  getAdminById(id: Types.ObjectId): Promise<Admin | undefined>;
  getAdminByName(name : string): Promise<Admin | undefined>;
  getAdminByEmail(email : string): Promise<Admin | undefined>;
  getAdminByToken(token:string): Promise<Admin | undefined>;
  updateCurrentAdmin(admin : Admin): Promise<void>;
}
