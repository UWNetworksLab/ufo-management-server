Polymer({
  is: "ufo-sidebar",
  ready: function() {
    this.pages = [
    {"href": "/", "text": "Home"},
    {"href": "/user", "text": "Users"},
    {"href": "/proxyserver/list", "text": "Proxy Servers"},
    {"href": "/setup", "text": "Setup"},
    {"href": "/sync", "text": "Sync Notifications"},
    {"href": "/logout", "text": "Logout"}
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
