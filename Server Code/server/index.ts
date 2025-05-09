import { createServer } from './server'

(async () => {
    const server = await createServer()
    server.listen(process.env.PORT , () => {console.log("server started")})
})();