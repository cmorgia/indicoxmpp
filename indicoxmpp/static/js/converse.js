require(['converse'], function (converse) {
    $(function () {
        if (currentUser!='') {
            $('.page-scroll a').bind('click', function (event) {
                var $anchor = $(this);
                $('html, body').stop().animate({
                    scrollTop: $($anchor.attr('href')).offset().top
                }, 700, 'easeInOutExpo');
                event.preventDefault();
            });
            var parser = document.createElement('a');
            parser.href = Indico.Urls.Base;
            var baseHost = parser.hostname;

            var xmppPort = 5280;

            converse.initialize({
                bosh_service_url: 'http://'+baseHost+':'+xmppPort+'/http-bind', // Please use this connection manager only for testing purposes
                i18n: locales['en'], // Refer to ./locale/locales.js to see which locales are supported
                keepalive: true,
                message_carbons: false,
                play_sounds: false,
                debug: true,
                roster_groups: true,
                show_controlbox_by_default: true,
                xhr_user_search: false,
                allow_registration: true,
                prebind: true,
                prebind_url: Indico.Urls.Base+'/xmpp/prebind',
                jid: currentUser+"@" + baseHost
            });
        }
    });
});



