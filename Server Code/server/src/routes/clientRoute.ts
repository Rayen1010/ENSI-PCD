import asyncHandler from 'express-async-handler';
import { Router } from "express";
import { 
    signinClientHandler,
    signupClientHandler,
    getReceiptsHandler

} from '../handlers/clientHandler';
import { jwtParseMiddleware } from '../middlewares/authMiddleware';

const router = Router()
router.post('/sign-in', asyncHandler(signinClientHandler))
router.post('/sign-up', asyncHandler(signupClientHandler))
router.get('/get-receipts', jwtParseMiddleware, asyncHandler(getReceiptsHandler))
module.exports = router