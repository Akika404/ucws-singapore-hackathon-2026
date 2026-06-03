import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import https from 'node:https'
import httpProxy from 'http-proxy'
import forge from 'node-forge'

const HTTP_PORT = 3007
const HTTPS_PORT = 3443

/** Generate a self-signed cert and start an HTTPS reverse proxy */
function httpsProxyPlugin() {
  return {
    name: 'https-proxy',
    configureServer(server: any) {
      const pki = forge.pki
      const keys = pki.rsa.generateKeyPair(2048)
      const cert = pki.createCertificate()
      cert.publicKey = keys.publicKey
      cert.serialNumber = '01'
      cert.validity.notBefore = new Date()
      cert.validity.notAfter = new Date()
      cert.validity.notAfter.setFullYear(cert.validity.notBefore.getFullYear() + 1)
      const attrs = [{ name: 'commonName', value: 'localhost' }]
      cert.setSubject(attrs)
      cert.setIssuer(attrs)
      cert.sign(keys.privateKey)

      const keyPem = pki.privateKeyToPem(keys.privateKey)
      const certPem = pki.certificateToPem(cert)

      const proxy = httpProxy.createProxyServer({
        target: `http://localhost:${HTTP_PORT}`,
        changeOrigin: true,
        ws: true,
      })

      const httpsServer = https.createServer(
        { key: keyPem, cert: certPem },
        (req: any, res: any) => {
          proxy.web(req, res, {}, () => {
            res.writeHead(502)
            res.end('Bad Gateway')
          })
        },
      )

      httpsServer.on('upgrade', (req: any, socket: any, head: any) => {
        proxy.ws(req, socket, head)
      })

      server.httpServer.on('listening', () => {
        httpsServer.listen(HTTPS_PORT, '0.0.0.0', () => {
          console.log(`  ➜  HTTPS proxy: https://localhost:${HTTPS_PORT}`)
        })
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), httpsProxyPlugin()],
  server: {
    host: '0.0.0.0',
    port: HTTP_PORT,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
      },
    },
  },
})
