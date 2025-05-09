import { Client, Item } from "../types/Client";

// for client
export interface SignInRequest { 
    login? : string;
    password? : string;
}
export interface SignInResponse {
    message? : string;
    client : Client;
    jwt : string;
}

export interface SignUpRequest { 
    userName? : string;
    email? : string;
    password? : string;
    card_Id? : string;
}
export interface SignUpResponse {
    message? : string;
}

export interface GetRequest {
    jwt : string;
}
export interface GetResponse {
    message? : string;
    client : Pick<Client, 'box'|
                   'entry_date'|
              'processing_date'|
                       'credit'|
                 'total_amount'>;
}

// for Admin
export interface AffectRequest {
    customer_Id? : string;
}

export interface AffectResponse {
    message? : string;
}

export interface RetRequest {
    customer_Id? : string;
    box? : Item[];
    entry_date? : Date;
    processing_date? : Date;
    total_amount? : number;
}

export interface RetResponse {
    message? : string;
}