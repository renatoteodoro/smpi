# Traefik — SMPI

O Traefik está **embutido no `stack.yml`** como serviço `traefik`. Não é necessário um stack separado.

## Pré-requisitos

1. **Cloudflare DNS** gerenciando `techteo.com.br`
2. **API Token do Cloudflare** com permissão `Zone → DNS → Edit` na zona `techteo.com.br`
3. Secret Docker criado:
   ```bash
   printf '%s' "seu-cf-token" | docker secret create CLOUDFLARE_DNS_API_TOKEN -
   ```

## Certificado wildcard

O Traefik emite automaticamente `*.techteo.com.br` via ACME DNS-01/Cloudflare.
O certificado cobre todos os subdomínios: `www.techteo.com.br`, `traefik.techteo.com.br`, etc.

## Dashboard do Traefik

Acessível em `https://traefik.techteo.com.br` com basic auth.
Para gerar a senha do basic auth:
```bash
htpasswd -nb admin senha_forte
# Exemplo de saída: admin:$apr1$xyz...
# Cole o hash no label traefik.http.middlewares.traefik-auth.basicauth.users do stack.yml
```

## IPs confiáveis do Cloudflare

Os IPs do Cloudflare que o Traefik aceita como proxy estão embutidos no `stack.yml`.
Atualize periodicamente em: https://www.cloudflare.com/ips/

## Verificação pós-deploy

```bash
# Certificado wildcard emitido corretamente
echo | openssl s_client -servername www.techteo.com.br -connect www.techteo.com.br:443 2>/dev/null \
  | openssl x509 -noout -subject -ext subjectAltName

# Redirect http → https funcionando
curl -I http://www.techteo.com.br/health/

# App respondendo via HTTPS
curl -fsS https://www.techteo.com.br/health/
```
