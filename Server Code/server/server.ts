import express from 'express'
import { initDb } from './src/dao';
import { errHandler } from './src/middlewares/errorMiddleware';
import { loggerMiddleware } from './src/middlewares/loggerMiddleware';
import { config } from 'dotenv'
const cors = require('cors')
export async function createServer(logRequests = true) {
    await initDb()
    config()
    const app = express()
    app.use(cors())
    app.use(express.json())
    if(logRequests) app.use(loggerMiddleware)

    app.use('/api/pcd0/admin',   require('./src/routes/adminRoute'))
    app.use('/api/pcd0/client',  require('./src/routes/clientRoute'))

    app.use(errHandler)
    return app
}