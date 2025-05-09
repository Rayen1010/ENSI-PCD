import asyncHandler from 'express-async-handler';
import { Router } from 'express'
import { affectClientIdHandler,
         updateClientHandler
} from '../handlers/adminHandler';

const router = Router()
router.post('/affect-id', asyncHandler(affectClientIdHandler)) 
router.post('/retrieve', asyncHandler(updateClientHandler)) 
module.exports = router