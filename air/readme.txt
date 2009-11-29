#Files where placed server url
-js/URLS.js
 var root = 'Http://...'

-html/main.html
 sandboxRoot attribute of sandbox iframe

#Create serteficate. 321654 is password
adt -certificate -cn ADigitalID 1024-RSA SigningCert.p12 321654

#Cretae instalation file
adt -package -storetype pkcs12 -keystore SigningCert.p12 cl.air application.xml css/ html/ icons/ js/ lib/ swf/


#Updating

In main.html is path to update.xml, where is set last version of application and
path to application. Application.xml of new version must have the same version
with update.xml.