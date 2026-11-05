# Home Mini PC Automator

Controle o seu PC com Windows 11 por voz, usando o Google Home Mini, ou por um painel visual no próprio PC.

## O que faz

- **Voz para PC:** você fala com o Google Assistente e o PC abre programas e jogos (Valorant, League, Brave, VS Code, Steam, Spotify, WhatsApp e outros).
- **Desligar o PC por voz:** "PC em 0%" desliga o computador depois de 30 segundos (dá para cancelar).
- **Painel visual:** janela no PC com um botão para cada programa, onde você também liga/desliga o servidor, adiciona apps novos e muda a porcentagem de voz de cada um.
- **Home Mini fala no PC:** o `cast_service.py` faz o Home Mini falar mensagens usando o `pychromecast`.

## Como funciona

1. Você fala com o Google Home. Exemplo: "Ok Google, brilho do PC em 30%".
2. O Google manda o pedido para o **Sinric Pro**, que trata o "PC" como uma lâmpada com brilho.
3. O servidor no PC (`main.py` + `sinric_service.py`) está conectado ao Sinric, recebe o número e procura qual programa tem essa porcentagem.
4. O `commands.py` abre o programa no Windows.

Não precisa de túnel nem de IFTTT. Cada programa vira uma porcentagem do mesmo dispositivo "PC", e o Sinric grátis aceita até 3 dispositivos.

## Arquivos

| Arquivo | Para que serve |
|---|---|
| `painel.pyw` | Painel visual. Liga o servidor sozinho ao abrir |
| `main.py` | Servidor FastAPI (rotas `/health`, `/comandos`, `/executar`) |
| `commands.py` | Comandos que abrem os programas e desligam o PC |
| `sinric_service.py` | Recebe o pedido do Google pelo Sinric Pro |
| `cast_service.py` | Faz o Home Mini falar (pychromecast) |
| `descobrir_dispositivos.py` | Descobre o nome do Home Mini na rede |
| `config.py` | Lê as configurações do `.env` |
| `niveis.json` | Porcentagem de voz de cada programa |
| `apps.json` | Apps adicionados pelo painel (criado sozinho) |
| `servidor.log` | Registro do servidor ligado pelo painel (criado sozinho) |

## Instalação

1. Abra o PowerShell **dentro da pasta do projeto** e instale tudo:

   ```
   pip install -r requirements.txt
   ```

2. Copie o `.env.example` para `.env` e preencha:

   ```
   API_SECRET_TOKEN=uma-senha-sua
   CAST_NAME=Setup
   SINRIC_APP_KEY=...
   SINRIC_APP_SECRET=...
   SINRIC_ID_PC=...
   ```

   - `CAST_NAME` é o nome do Home Mini na rede. Para descobrir, rode `python descobrir_dispositivos.py`.
   - As chaves do Sinric ficam no painel do Sinric Pro. O `SINRIC_ID_PC` é o ID do dispositivo "PC" (tipo *Switch with Dimming*).

3. No app Google Home, vincule o Sinric Pro e confirme que o dispositivo "PC" aparece.

## Como usar

### Pelo painel

Dê dois cliques no `painel.pyw`.

- **Ligar / Desligar:** controla o servidor. Ele liga sozinho ao abrir o painel.
- **Botão do programa:** abre o programa na hora.
- **Número ao lado:** porcentagem de voz do programa. Mude e clique em **Salvar porcentagens**. Vale na hora, sem reiniciar.
- **+ Adicionar app:** escolha o `.exe` ou um atalho, dê um nome e uma porcentagem. Use o **✕** para remover.
- **Desligar PC (30s) / Cancelar:** desliga ou cancela o desligamento.

Para o painel abrir junto com o Windows: aperte `Win + R`, digite `shell:startup` e coloque um atalho do `painel.pyw` lá.

### Por voz

Diga "Ok Google, brilho do PC em **N**%". O N é a porcentagem do programa. Exemplos iniciais:

| % | Programa |
|---|---|
| 10 | Valorant |
| 20 | League of Legends |
| 30 | Brave |
| 40 | Brave anônimo |
| 50 | VS Code |
| 60 | Steam |
| 70 | Bloco de notas |
| 80 | WhatsApp |
| 90 | Spotify |
| **0** | **Desliga o PC (30 segundos)** |

Regras das porcentagens: use números de 5 a 100, com pelo menos 5 de diferença entre eles. O servidor aceita um erro de até 2 para mais ou para menos. O 0 é só para desligar.

## Dicas

- Ligar o PC por voz não funciona, porque um PC desligado não escuta a rede. Para isso seria preciso Wake-on-LAN ou uma tomada inteligente.
- Se o servidor não ligar, olhe o `servidor.log`.
- Mudou algum arquivo `.py`? Feche e abra o painel de novo. Mudar porcentagens e apps não precisa reiniciar.
- Só um servidor pode rodar por vez. Se ele já foi ligado pelo VS Code ou outro método, o painel não consegue desligá-lo.

## Segurança

- Nunca suba o `.env` para o GitHub. Ele tem a senha da API e as chaves do Sinric.
- O `apps.json` e o `servidor.log` mostram caminhos do seu PC. Mantenha fora do GitHub também.
- As rotas `/comandos` e `/executar` pedem o cabeçalho `X-API-Key` com o seu `API_SECRET_TOKEN`.
