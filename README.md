# Kard Private Api
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
![](https://komarev.com/ghpvc/?username=ghrlt-kard-private-api&color=brightgreen&label=Repository%20views)  

Python wrapper of Kard neobank private API

Made with the help [HTTP Toolkit](https://httptoolkit.tech/) for trafic sniffing <3 It's an awesome tool!


## Installation
`git clone https://github.com/ghrlt/kard-private-api`<br>
`cd kard-private-api`

Open `secrets.json` and replace the values of `accountPin` & `accountTel` with yours.<br>
When using the API, be sure to initialize the `Kard` class **and** to call `init()` method on it.
```python
import v2

k = v2.Kard()
k.init()
...
```

**You're ready!**<br>
Checkout some examples to get started: [Examples](https://github.com/ghrlt/kard-private-api/examples)


### How does it login to my Kard account?

The login processus include:
	- Generating a unique identifier, linked to your account
	- If new uid, confirm sms otp
	- Confirm PIN code
Then, and only then, we have the `accessToken` and `refreshToken`.

The wrapper will automatically create and store your uid and obtain and store your tokens

ALL YOU NEED TO ENSURE IS THAT YOU PROVIDE GOOD VALUES FOR YOUR TEL NUMBER AND PIN CODE IN `secrets.json`


## License

[GNU GPLv3](https://github.com/ghrlt/kard-private-api/blob/master/LICENSE)

## Disclaimer
I shall not, and will not be liable for any misuse or unauthorised use, leading or not to damage to any third-party.
This API is to be used for educational purposes only.


## Support me
<a href="https://s.kard.eu/ghrlt/5.0"><img alt="Support me through bank card" src="https://www.svgrepo.com/show/301678/piggybank-pig.svg" href="https://s.kard.eu/ghrlt/5.0" width="40" height="40"></a>
<a href="https://discord.gg/cQY9hc7XHm"><img alt="Send me a Discord Nitro" src="https://discord.com/assets/f8389ca1a741a115313bede9ac02e2c0.svg" href="https://discord.gg/cQY9hc7XHm" width="40" height="40"></a>
<a href="https://kard.eu?r=GAEHER"><img alt="Subscribe to Kard" src="https://uploads-ssl.webflow.com/5fc53498e2555190106eb531/5fc5a6996e50deb8447505e4_logo-purple.svg" href="https://kard.eu?r=GAEHER" width="40" height="40"></a>
