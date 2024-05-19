# QuarterMaster
![QuarterMaster Banner Image](Marketing/banner.png)
QuarterMaster is a smart kitchen device used to track grocery inventory, expiration dates, and suggest recipes to minimize food waste.

More details can be found at our [website](https://oliverstratford23.wixsite.com/quartermaster).

### QuarterMaster Repository Structure
Current development work is organized as follows:

| Directory | Info |
|--|--|
| `/App` | Holds all server-side files for the Raspberry Pi |
| `/App/website` | Holds all client-side web app files |
| `/CAD` | Holds any CAD and STL files, parts lists, and assembly instructions. |
| `/Marketing` | Holds marketing briefs, website files, blender files/renders, etc. |

### Client and Server Info
The physical scanner device, running on a RPi, hosts a local HTTP webserver allowing clients to connect directly via IP address on port 8000.
For example, if the RPi's local IP address was 192.168.0.14, another device on the same network could access the webclient via http://192.168.0.14:8000. Note this does not work on networks with certain firewalls/restrictions (notably including Bath Spa `eduroam` and similar networks, depending on subdomain allocations). It is expected to work on most home networks.

> **Note:** Port number may be redefined in server.py

For reference during development, the following figure summarizes the platforms, languages, and responsibilities of each entity.

|| Client | Server |
|--|--|--|
| **Platform** | Mobile/Desktop Browser | Raspberry Pi 5 |
| **Languages** | <li>HTML</li><li>CSS</li><li>JS</li> | Python
| **Features** |<li>Inventory Viewing</li><li>Recipe Viewing</li> | <li>Scan Items In</li><li>Scan Items Out</li>


### Communications Protocol
Client ↔ Server communication uses HTTP protocol. Specifically, GET and POST requests are made by the client.
> This functionality is implemented in `/App/server.py` and `/App/website/client.js`

| Type | Path | Body | Response Content Type| Response | Note|
|--|--|--|--|--|--|
| `GET` | `/index.html` | |  `text/html`  | `index.html` file |
| `GET` | `/styles.css` || `text/css`  | `styles.css` file |
| `GET` | `/client.js` | |`application/javascript`  | `client.js` file |
| ... | ... | ... | ... | ...| Continued for any additional plain files
| `GET` | `/inventory` || `application/javascript` | JSON inventory data | |
| `GET` | `/recipe/*` || `application/javascript` | Makes request to Tesco API and returns result. | See `server.py` line 180-225 for additional parameter details.
| `POST` | `/update-inventory` | Updated JSON inventory data | `text/html` | Status Message | Current web app version does not implement this functionality.

