import { AffectRequest,
         AffectResponse,
         RetRequest,
         RetResponse
} from '../../../shared/src/APIs/api'
import { ExpressHandler } from "../types"
import { db } from '../dao';

export const affectClientIdHandler : ExpressHandler<
AffectRequest,
AffectResponse
> = async (req, res) => {
    const { customer_Id } = req.body

    const client = await db.getClientByCId("none");
    if(!client) {
        return res.status(404).send({error: 'not found'})
    }
    if(customer_Id){
        client.customer_Id = customer_Id
        await db.updateCurrentClient(client)
        return res.status(200).json({ message: 'customer Id affected successful' });
    }
    else{
       return res.status(400).json({ error: 'customer_Id is required' });
    }
}

export const updateClientHandler: ExpressHandler<
RetRequest,
RetResponse
> = async (req, res) => {
    const { customer_Id, box, entry_date, processing_date, total_amount } = req.body;
    const client = await db.getClientByCId(customer_Id!);
    if(!client) {
        return res.status(404).send({error: 'not found'})
    }
    if(customer_Id){
        client.box = box
        client.entry_date = entry_date
        client.processing_date = processing_date
        client.total_amount = total_amount
        client.credit = client.credit! - total_amount!
        await db.updateCurrentClient(client)
        return res.status(200).json({ message: 'client updated successful' });
    }
    else{
       return res.status(400).json({ error: 'customer_Id is required' });
    }
}