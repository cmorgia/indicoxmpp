from wtforms import StringField, IntegerField

from MaKaC.authentication import AuthenticatorMgr
from MaKaC.user import LoginInfo
from MaKaC.webinterface import urlHandlers
from MaKaC.webinterface.rh.base import RH
from MaKaC.webinterface.rh.login import RHSignInBase
from MaKaC.webinterface.urlHandlers import SecureURLHandler
from boshclient import BOSHClient
from indico.core.config import Config
from indico.core.plugins import IndicoPluginBlueprint, IndicoPlugin, plugin_engine
from flask import session, request
from indico.core import signals
from indico.web.forms.base import IndicoForm

blueprint = IndicoPluginBlueprint('indicoxmpp', __name__, url_prefix='/xmpp')


class SettingsForm(IndicoForm):
    base_host = StringField(label='XMPP Host name', description='Specify the XMPP Host name.',default="localhost")
    base_port = IntegerField(label='XMPP Port', description='Specify the XMPP Port.',default="5280")


class IndicoXMPPPlugin(IndicoPlugin):
    """Indico XMPP Plugin

    """
    configurable = True
    settings_form = SettingsForm

    def init(self):
        super(IndicoXMPPPlugin, self).init()

        self.inject_js('indicoxmpp_js')
        self.inject_css('indicoxmpp_css')


    def register_assets(self):
        self.register_js_bundle('indicoxmpp_js' ,'js/lib/*.js','js/converse.js')
        self.register_css_bundle('indicoxmpp_css', 'css/conversejs/converse.css')


    def get_blueprints(self):
        return blueprint

    @signals.app_created.connect
    def _config(app, **kwargs):
        pass


class RHSignInNoUI( RHSignInBase ):
    def _checkParams( self, params ):
        params = request.json
        self._login = str(params[u'login'])
        self._password = str(params[u'password'])

    def _process(self):
        #Check for automatic login
        authManager = AuthenticatorMgr()
        if (authManager.isSSOLoginActive() and len(authManager.getList()) == 1 and
           not Config.getInstance().getDisplayLoginPage()):
            self._redirect(urlHandlers.UHSignInSSO.getURL(authId=authManager.getDefaultAuthenticator().getId()))
            return

        li = LoginInfo( self._login, self._password )
        av = authManager.getAvatar(li)
        self._responseUtil.content_type='application/json'
        if not av:
            return '{"success":false,"message":"User not authenticated or found"}'
        elif not av.isActivated():
            return '{"success":false,"message":"User not activated"}'
        else:
            return '{"success":true}'


class RHPrebind(RH ):

    def _process(self):
        import json
        jid = session["_jid"]
        sid = session["_sid"]
        rid = session["_rid"]
        result = {'jid': jid, 'rid': rid, 'sid': sid}
        self._responseUtil.content_type='application/json'
        return json.dumps(result)


class RHExists(RHSignInBase):
    def _checkParams(self, params):
        params = request.json
        self._login = str(params[u'login'])

    def _process(self):
        authManager = AuthenticatorMgr()
        if (authManager.isSSOLoginActive() and len(authManager.getList()) == 1 and
           not Config.getInstance().getDisplayLoginPage()):
            self._redirect(urlHandlers.UHSignInSSO.getURL(authId=authManager.getDefaultAuthenticator().getId()))
            return

        av = authManager.getAvatarByLogin(self._login).values()[0]
        self._responseUtil.content_type='application/json'
        if not av:
            return '{"success":false,"message":"User not found"}'
        elif not av.isActivated():
            return '{"success":false,"message":"User not activated"}'
        else:
            return '{"success":true}'


class UHSignInNoUI(SecureURLHandler):
    _endpoint = "user.signIn-noui"


class UHPrebind(SecureURLHandler):
    _endpoint = "user.prebind"


class UHExists(SecureURLHandler):
    _endpoint = "user.exists"


# XMPP Prebind support
blueprint.add_url_rule('/prebind', 'prebind', RHPrebind)

# Exists
blueprint.add_url_rule('/exists', 'exists', RHExists,methods=('GET', 'POST'))

# Sign in
blueprint.add_url_rule('/login/noui', 'signIn-noui', RHSignInNoUI, methods=('POST',))


def decorateMakeLoginProcess(fn):
    def new_funct(*args, **kwargs):
        ret = fn(*args, **kwargs)
        if request.method=='POST':
            try:
                plugin = plugin_engine.get_plugin("indicoxmpp")
                self = args[0]
                base_host = plugin.settings.get("base_host")
                base_port = plugin.settings.get("base_port")
                jid = self._login+"@"+base_host
                service = "http://{0}:{1}/http-bind".format(base_host,base_port)
                c = BOSHClient(service, jid, self._password)
                c.init_connection()
                c.request_bosh_session()
                if c.authenticate_xmpp():
                    session["_rid"] = str(c.rid)
                    session["_sid"] = str(c.sid)
                    session["_jid"] = str(c.jid)
                    session["currentUser"]=self._login

                c.close_connection()
            except Exception as e:
                pass
        return ret

    return new_funct

RHSignInBase._makeLoginProcess = decorateMakeLoginProcess(RHSignInBase._makeLoginProcess)