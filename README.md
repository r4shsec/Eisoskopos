# EISOSKOPOS
## ⚠️ Disclaimer

> **For Educational & Awareness Purposes Only**  
> Please **do not use** this script for unauthorized or malicious activities.  
> The author **assumes no responsibility** for misuse or consequences.  
> Always act **responsibly and within the law**.

> _"Safer Internet, Safer World"_  
> — @r4shsec

---

## 📂 Browser LevelDB Paths

| Browser / App      | Path                                                                 |
|--------------------|----------------------------------------------------------------------|
| 🌐 **Brave**       | `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Local Storage\leveldb` |
| 🌐 **Chrome**      | `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Local Storage\leveldb` |
| 🌐 **Edge**        | `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Local Storage\leveldb` |
| 🌐 **Opera**       | `%APPDATA%\Opera Software\Opera Stable\Local Storage\leveldb`        |
| 🌐 **Vivaldi**     | `%APPDATA%\Vivaldi\User Data\Default\Local Storage\leveldb`          |
| 🌐 **Yandex**      | `%APPDATA%\Yandex\YandexBrowser\User Data\Default\Local Storage\leveldb` |
| 🔒 **Discord**     | `%APPDATA%\discord\Local Storage\leveldb`                            |
| 🔒 **Discord PTB** | `%APPDATA%\discordptb\Local Storage\leveldb`                         |
| 🔒 **Discord Canary** | `%APPDATA%\discordcanary\Local Storage\leveldb`                   |

---

## 🕓 Browser History Paths

| Browser / App  | Path                                                        |
|----------------|-------------------------------------------------------------|
| 🌐 **Chrome**  | `%LOCALAPPDATA%\Google\Chrome\User Data\Default\History`    |
| 🌐 **Brave**   | `%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\History` |
| 🌐 **Edge**    | `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History`   |
| 🌐 **Opera**   | `%APPDATA%\Opera Software\Opera Stable\History`             |
| 🌐 **Vivaldi** | `%APPDATA%\Vivaldi\User Data\Default\History`               |
| 🌐 **Yandex**  | `%APPDATA%\Yandex\YandexBrowser\User Data\Default\History`  |

---

## ❓ Q&A

<details>
<summary>👀 <strong>What is this?</strong></summary>

This script demonstrates how malicious actors could retrieve a Discord account and other sensitive data.
</details>

<details>
<summary>🤯 <strong>How!?</strong></summary>

Discord stores your account **token** in LevelDB `.ldb` files in plain text.  
Anyone with access can extract sensitive information.
</details>

<details>
<summary>💡 <strong>Does 2FA Secure It?</strong></summary>

**No.** Two-Factor Authentication does not protect your locally stored token.  
A malicious actor could still access your Discord account.
</details>

<details>
<summary>🔑 <strong>What other info can malicious actors get?</strong></summary>

Malicious actors could obtain **much more** information than this script demonstrates.  
This is only a proof-of-concept.
</details>

<details>
<summary>👆 <strong>Can malicious actors login using my Discord account token?</strong></summary>

**Yes.** Malicious actors could log in to your Discord account using a script like this:

```js
let token = "YOUR_DISCORD_TOKEN";
function login(token) {
    setInterval(() => {
        document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage.token = `"${token}"`;
    }, 50);
    setTimeout(() => {
        location.reload();
    }, 2500);
}
login(token);
```
</details>

---

## 🛡️ Defense

### 1. Before you download any files, scan them using [Virustotal](https://www.virustotal.com/gui/home/upload)
### 2. Use a Windows password to keep all browser passwords safe #
