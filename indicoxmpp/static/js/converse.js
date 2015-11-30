require(['converse'], function (converse) {
    $(function () {
        if (currentUser!='') {
            $(window).scroll(function () {
                if ($(".navbar").offset().top > 50) {
                    $(".navbar-fixed-top").addClass("top-nav-collapse");
                } else {
                    $(".navbar-fixed-top").removeClass("top-nav-collapse");
                }
            });
            //jQuery for page scrolling feature - requires jQuery Easing plugin
            $('.page-scroll a').bind('click', function (event) {
                var $anchor = $(this);
                $('html, body').stop().animate({
                    scrollTop: $($anchor.attr('href')).offset().top
                }, 700, 'easeInOutExpo');
                event.preventDefault();
            });
            var parser = document.createElement('a');
            parser.href = baseUrl;
            var baseHost = parser.hostname;

            var xmppPort = 5280;

            converse.initialize({
                bosh_service_url: 'http://'+baseHost+':'+xmppPort+'/http-bind', // Please use this connection manager only for testing purposes
                i18n: locales['en'], // Refer to ./locale/locales.js to see which locales are supported
                keepalive: true,
                message_carbons: true,
                play_sounds: true,
                roster_groups: true,
                show_controlbox_by_default: true,
                xhr_user_search: false,
                allow_registration: true,
                prebind: true,
                prebind_url: '/indico/xmpp/prebind',
                jid: "fake@" + baseHost
            });
        }
    });
});



