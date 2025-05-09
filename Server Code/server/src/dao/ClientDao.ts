import { Types } from 'mongoose';
import { Client } from '../../../shared/src/types/Client';

export interface ClientDao {
  createClient(client : Client): Promise<void>;
  deleteClient(id: Types.ObjectId): Promise<void>; 
  getClientById(id: Types.ObjectId): Promise<Client | undefined>;
  getClientByCardId(cardId: string): Promise<Client | undefined>;
  getClientByCId(cId: string): Promise<Client | undefined>;
  getClientByName(name: string): Promise<Client | undefined>;
  getClientByEmail(email: string): Promise<Client | undefined>;
  countClients() : Promise<number>;
  withdraw(id: Types.ObjectId, fees: number): Promise<void>;
  updateCurrentClient(client : Client): Promise<void>;
}