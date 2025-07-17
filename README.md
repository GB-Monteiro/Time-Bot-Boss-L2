# 🤖 Lineage 2 Boss Respawn Bot

Um bot para Discord que monitora o tempo de morte e respawn aleatório dos bosses no jogo **Lineage 2**.  
Ele envia alertas automáticos quando o boss entra na janela de respawn.

---

## ⚙️ Funcionalidades

- ✅ Comandos para registrar morte do boss (`!boss died <nome>`)
- ⏰ Cálculo automático do tempo de respawn aleatório
- 📢 Alerta em canal específico no Discord quando começa a janela de respawn
- 🧹 Remoção automática após fim do respawn
- 💾 Armazenamento persistente em `boss_data.json`
- 🌐 Mantido vivo por Flask (`/` route) para hosting gratuito

---

## 🛠️ Comandos Disponíveis

| Comando                 | Descrição                                                                 |
|------------------------|---------------------------------------------------------------------------|
| `!boss died <nome>`     | Registra a morte do boss e inicia contagem para respawn                  |
| `!bossstatus`           | Mostra status atual de todos os bosses registrados                       |
| `!cancelboss <nome>`    | Remove um boss da lista de status                                         |
| `!setboss <nome> <HH:MM>` | Define manualmente o horário da morte do boss (UTC-3)                   |
| `!nextrespawn`          | Mostra o próximo boss que entrará em janela de respawn                   |
| `!listbosses`           | Lista os bosses monitorados                                               |

---

## 🧠 Bosses Configurados

| Nome       | Respawn Aleatório (Horas) |
|------------|----------------------------|
| Queen Ant  | 21h → 23h                  |
| Core       | 20h → 24h                  |
| Orfen      | 18h → 26h                  |
| Zaken      | 16h → 28h                  |

---

## 🚀 Como Hospedar no Render

### 1. Faça fork/clonagem deste repositório

```bash
git clone https://github.com/SEU_USUARIO/NOME_REPOSITORIO.git
