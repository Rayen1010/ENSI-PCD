import { 
        SignInRequest,
        SignInResponse,
        SignUpRequest,
        SignUpResponse,
        GetRequest,
        GetResponse
} from '../../../shared/src/APIs/api'
import { ERRORS } from '../../../shared/src/errors'
import { ExpressHandler } from "../types"
import { Client } from '../../../shared/src/types/Client'
import { db } from '../dao';
import { hashPassword } from '../env';
import { signJwt } from '../auth';
import { ObjectId } from '../../../shared/src/connection';

export const signinClientHandler : ExpressHandler< 
SignInRequest,
SignInResponse
> = async (req, res) => {
    const { login , password } = req.body
    if(!login || !password){
        return res.status(400).send({error:'all fields are required'})
    }
    const existing = (await db.getClientByName(login)) || (await db.getClientByEmail(login))
    if(!existing || existing.password !== hashPassword(password)){
        return res.status(403).send({error: 'unauthorized'})
    }
    const jwt = signJwt({clientId : existing._id!})
    // Store JWT in cookie or local storage or session storage
    // res.cookie('jwt', jwt);
    res.status(200).send({
        message : existing.userName,
        client : existing,
        jwt
    })    
}

export const signupClientHandler : ExpressHandler< 
SignUpRequest,
SignUpResponse
> = async (req, res) => {
    const { userName , email , password, card_Id } = req.body
    if(!userName || !email || !password || !card_Id)
        return res.status(400).send({error:'all fields are required'})

    if (await db.getClientByName(userName)) {
      return res.status(403).send({ error: ERRORS.DUPLICATE_USERNAME });
    }
    if (await db.getClientByEmail(email)) {
        return res.status(403).send({ error: ERRORS.DUPLICATE_EMAIL });
    }
    const newClient : Client = {
        userName,
        email,
        password : hashPassword(password!),
        card_Id
    }    
    await db.createClient(newClient)
    res.status(200).send({ message : 'Client Was Created Successfully' });
}

export const getReceiptsHandler : ExpressHandler< 
GetRequest,
GetResponse
> = async (req, res) => {
    const clientId = res.locals.clientId;
    if (clientId) {
        const client = await db.getClientById(new ObjectId(clientId));
        if(!client)
            return res.status(400).send({error:'Client not found'})
        return res.status(200).send({
            message : 'retrieving successfully!',
            client : client
        });
    } else {
        return res.status(403).send({error: 'unauthorized'})
    }
}