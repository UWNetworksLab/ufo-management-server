Polymer({
  is: "ufo-sidebar",
  properties: {
    homePage: String,
    logoutPage: String,
    proxyServerPage: String,
    setupPage: String,
    syncNotificationPage: String,
    userPage: String,
  },
  ready: function() {
    this.pages = [
      {"href": this.homePage, "text": "Home"},
      {"href": this.userPage, "text": "Users"},
      {"href": this.proxyServerPage, "text": "Proxy Servers"},
      {"href": this.setupPage, "text": "Setup"},
      {"href": this.syncNotificationPage, "text": "Sync Notifications"},
      {"href": this.logoutPage, "text": "Logout"}
    ];
  },
  itemClicked: function(e) {
    window.location.href = e.target.getAttribute("data-href");
  },
  currentPage: function(pages) {
    for (var i in pages) {
      if (pages[i].href == window.location.pathname) {
        return i;
      }
    }
  }
});
