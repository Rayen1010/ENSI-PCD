import { ClientDao } from "./ClientDao";
import { AdminDao } from "./AdminDao";
import { MongoDB } from "../dataStore/mongoDb";
import { connectDb } from "../../../shared/src/connection"

export interface DataStore extends 
    AdminDao, 
    ClientDao
{}

export let db: DataStore; 

export async  function initDb(): Promise<void> {
    connectDb()
    .then(() => { db = new MongoDB(); console.log('Connected to Database')})
    .catch((e) => console.log(e))
}