from decouple import config
import Usable.config as conf
from django.core.mail import send_mail


def forgetEmailPattern(data):
    try:
        html_content = f"""
                    <!doctype html>
            <html lang="en-US">

            <head>
                <meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
                <title>Reset Password Email Template</title>
                <meta name="description" content="Reset Password Email Template.">
                
            </head>

            <body marginheight="0" topmargin="0" marginwidth="0" style="margin: 0px; background-color: #f2f3f8;" leftmargin="0">
                
                <!--100% body table-->
                <table cellspacing="0" border="0" cellpadding="0" width="100%" bgcolor="#f2f3f8"
                    style="@import url(https://fonts.googleapis.com/css?family=Rubik:300,400,500,700|Open+Sans:300,400,600,700); font-family: 'Open Sans', sans-serif;">
                    <tr>
                        <td>
                            <table style="background-color: #f2f3f8; max-width:670px;  margin:0 auto;" width="100%" border="0"
                                align="center" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="height:80px;">&nbsp;</td>
                                </tr>
                                <!-- <tr>
                                    <td style="text-align:center;">
                                    <a href="https://rakeshmandal.com" title="logo" target="_blank">
                                        <img width="280" height="280" src="./Group 603.png" title="logo" alt="logo">
                                    </a>
                                    </td>
                                </tr> -->
                                <tr>
                                    <td style="height:20px;">&nbsp;</td>
                                </tr>
                                <tr>
                                    <td>
                                        <table width="95%"   border="0" align="center" cellpadding="0" cellspacing="0"
                                            style="max-width:670px;
                                                height: 400px;
                                            background:#fff; border-radius:3px; text-align:center;-webkit-box-shadow:0 6px 18px 0 rgba(0,0,0,.06);-moz-box-shadow:0 6px 18px 0 rgba(0,0,0,.06);box-shadow:0 6px 18px 0 rgba(0,0,0,.06);">
                                            <tr>
                                                <td style="padding:0 35px;">
                                                    <h1 style="color:#127DB3;
                                                    padding-bottom: 20px;
                                                    font-weight:500; margin:0;font-size:28px;font-family:'Rubik',sans-serif;">You have requested to reset your password</h1>
                                                    <span
                                                        style="display:inline-block; vertical-align:middle; margin:29px 0 26px;    
                                                        padding-bottom: 20px;
                                                        border-bottom: 3px solid #000; width:270px;"></span>
                                                        <p style="color:#127DB3; font-size:19px;line-height:24px; margin:0;
                                                        padding-top: 10px;
                                                        ">
                                                            Your Verification Code is {data['token']}
                                                        </p>

                                                
                                                </td>
                                            </tr>
                                            <tr>
                                                <!-- <td style="height:40px;">&nbsp;</td> -->
                                                <td style="background-color: #127DB3;"  ><h5 style="color: #fff;">Copyright 2024 - All Right Reserved Kuber Services</h5></td>
                                                <!-- <td>Kuber services</td> -->
                                            </tr>
                                            <tr>
                                                <!-- <td style="height:40px;">&nbsp;</td> -->
                                            </tr>
                                        </table>
                                    </td>
                                <tr>
                                    <td style="height:20px;">&nbsp;</td>
                                </tr>
                                <!-- <tr>
                                    <td style="text-align:center;">
                                        <p style="font-size:14px; color:rgba(69, 80, 86, 0.7411764705882353); line-height:18px; margin:0 0 0;">&copy; <strong>www.rakeshmandal.com</strong></p>
                                    </td>
                                </tr> -->
                                <tr>
                                    <td style="height:80px;">&nbsp;</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
                <!--/100% body table-->
            </body>

            </html>
            """
        send_mail(
            data["subject"],
            "",
            data["EMAIL_HOST_USER"],
            [data["toemail"]],
            connection=conf.connection,
            fail_silently=False,
            html_message=html_content,
        )
        return True
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False
