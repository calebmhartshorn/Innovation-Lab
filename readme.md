### Repo Structure
All outdated code from last semester has been moved into `_Outdated`.
All current, ongoing work exists in the root directory.

### Client and Server Info
The physical scanner device, running on a RPi, hosts an HTTP webserver allowing clients to connect directly via local wlan IP address on port 8080.
For example, if the RPi's local IP address was 192.168.0.14, you could access the webclient via http://192.168.0.14:8080. Note this does not work on networks with certain firewalls/restrictions (noteably inlcuding Bath Spa `eduroam` and guest networks). It is expected to work on most home networks.

|| Client | Server |
|--|--|--|
| **Platform** | Mobile/Desktop Browser | Raspberry Pi 5 |
| **Languages** | <li>HTML</li><li>CSS</li><li>JS</li> | Python
| **Features** |<li>Manual Inventory Edits</li><li>Recipe Viewing</li> | <li>Scan Items In</li><li>Scan Items Out</li>


### Communications Protocol
Client ↔ Server communication uses HTTP protocol. Specifically, GET and POST requests are made by the client.
| Type | Path | Body | Response Content Type| Response | Note|
|--|--|--|--|--|--|
| `GET` | `/index.html` | |  `text/html`  | `index.html` file |
| `GET` | `/styles.css` || `text/css`  | `styles.css` file |
| `GET` | `/client.js` | |`application/javascript`  | `client.js` file |
| ... | ... | ... | ... | ...| Continued for any additional files
| `GET` | `/inventory` || `application/javascript` | JSON inventory data | |
| `GET` | `/recipe/*` || `application/javascript` | Makes request to Tesco API and returns result. | See `server.py` line 105-144 for additional parameter details.
| `POST` | `/update-inventory` | Updated JSON inventory data | `text/html` | Status Message |
