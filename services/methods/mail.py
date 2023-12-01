from django.conf import settings
from services.translations.en import en
from services.translations.es import es
router=settings.URL_FRONT
fonts="{font-family: Arial, sans-serif;}"

languages = {"es":es(), "en":en()}
images = {"es":"verificacion.png", "en":"verification.png"}
images_bienvenida = {"es":"bienvenido.png","en":"welcome.png"}

def change_password_mail(rando, language):
	return (
		f'''<!DOCTYPE html>
    <html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
    <head>
    	<meta charset="UTF-8">
    	<meta name="viewport" content="width=device-width,initial-scale=1">
    	<meta name="x-apple-disable-message-reformatting">
    	<title></title>
    	<!--[if mso]>
    	<noscript>
    		<xml>
    			<o:OfficeDocumentSettings>
    				<o:PixelsPerInch>96</o:PixelsPerInch>
    			</o:OfficeDocumentSettings>
    		</xml>
    	</noscript>
    	<![endif]-->
    	<style>
    		table, td, div, h1, p {fonts}
    	</style>
    </head>
    <body style="margin:0;padding:0;background-color:white;">
    	<table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:white;">
    		<tr>
    			<td align="center" style="padding:0;">
    				<table role="presentation" style="width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
    					<tr>
    						<td align="center" style="padding:20px 0 15px 0;">
    							<img  src="https://focushub.io/api/media/top.png" alt="" width="700" style="height:auto;display:block;" />
    						</td>
    					</tr>
    					<tr>
    						<td style="padding:26px 30px 42px 30px;">
    							<table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
    								<tr>
                                        <td style="background: #ffffff; text-align: center; padding: 18px 0 0 0;">
                                            <img src="https://focushub.io/api/media/{images[language]}" alt="" width="400" style="height: auto; display: block; margin: 0 auto;" />
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="background: #ffffff; text-align: center; padding: 18px 0 0 0; position: relative;">
                                            <p style="position: absolute; top: 20%; left: 50%; transform: translate(-50%, -50%); font-size: 40px; color: black;"><b>{rando}</b></p>
                                        </td>
                                    </tr>
                                   
                                    
                                    <br>
                                    <tr>
                                        <tr>
                                            <td style="background: #ffffff; text-align: center; padding: 5px 0 0 0;">
                                                <img src="https://focushub.io/api/media/linea.png" alt="" width="100%" style="height: auto; display: block; margin: 0 auto;" />
                                            </td>
                                        </tr>
                                        
                                        
    							</table>
    						</td>
                            <tr>
                                <td style="padding: 70px; background: white; width: 0; height: 0; padding-top: 0; padding-bottom: 0; padding-right: 0; padding-left: 0;">
                                    <img src="https://focushub.io/api/media/bottom.png" alt="" style="width: 100%; height: auto; display: block; object-fit: cover; object-position: 50 50;" />
                                </td>
                            </tr>
    				</table>
    			</td>
    		</tr>
    	</table>
    </body>
    </html>'''
	)

def mail_standar(rando, language):
	return (f'''<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="x-apple-disable-message-reformatting">
  <title></title>
  <!--[if mso]>
        <noscript>
                <xml>
                        <o:OfficeDocumentSettings>
                                <o:PixelsPerInch>96</o:PixelsPerInch>
                        </o:OfficeDocumentSettings>
                </xml>
        </noscript>
        <![endif]-->
  <style>
    		table, td, div, h1, p {fonts}
    	</style>
</head>

<body style="margin:0;padding:0;background-color:white;">
  <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:white;">
    <tr>
      <td align="center" style="padding:0;">
        <table role="presentation" style="width:100%;max-width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;">
          <tr>
            <td align="center" style="padding:20px 0 15px 0;">
              <img src="https://focushub.io/api/media/top.png" alt="" width="700" style="height:auto;display:block;" />
            </td>
          </tr>
          <tr>
            <td style="padding:26px 30px 42px 30px;">
              <table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;">
                <tr>
                  <td style="background: #ffffff; text-align: center; padding: 18px 0 0 0;">
                    <img src="https://focushub.io/api/media/{images_bienvenida[language]}" alt="" width="400" style="height: auto; display: block; margin: 0 auto;" />
                  </td>
                </tr>
                <tr>
                  <td style="background: #ffffff; text-align: center; padding: 18px 0 0 0; position: relative;">
                    <p style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 40px; color: black;"><b>{rando}</b></p>
                  </td>
                </tr>

                <tr>
                  <td style="padding: 40px 0 36px 0;">
                    <p style="margin: 0; color:#000000;font-size: 30px; line-height: 30px; font-family: Arial, sans-serif; text-align: center;">
                        {languages[language]['Estas a un paso de tener tu cuenta en']} <b>Focus</b>, {languages[language]['solo ingresa el código de arriba para confirmar tu correo electrónico']}.
                    </p>
                  </td>
                </tr>
                <tr>
                  <td style="background: #ffffff; text-align: center; padding: 5px 0 0 0;">
                    <img src="https://focushub.io/api/media/linea.png" alt="" width="100%" style="height: auto; display: block; margin: 0 auto;" />
                  </td>
                </tr>

              </table>
            </td>
          </tr>
          <tr>
                                <td style="padding: 70px; background: white; width: 0; height: 0; padding-top: 0; padding-bottom: 0; padding-right: 0; padding-left: 0;">
                                    <img src="https://focushub.io/api/media/bottom.png" alt="" style="width: 100%; height: auto; display: block; object-fit: cover; object-position: 50 50;" />
                                </td>
                            </tr>
        </table>
      </td>
    </tr>
  </table>
</body>

</html>
'''
	)	