"""App configs to simplify the importing for tests and mocks."""

PATHS = {
    'landing_page_path': '/',
    'user_page_path': '/user',

    'user_add_path': '/user/add',
    'user_delete_path': '/user/delete',
    'user_details_path': '/user/details',
    'user_get_invite_code_path': '/user/getInviteCode',
    'user_get_new_key_pair_path': '/user/getNewKeyPair',
    'user_toggle_revoked_path': '/user/toggleRevoked',

    'setup_oauth_path': '/setup',

    'proxy_server_add': '/proxyserver/add',
    'proxy_server_delete': '/proxyserver/delete',
    'proxy_server_edit': '/proxyserver/edit',
    'proxy_server_list': '/proxyserver/list',

    'cron_proxy_server_distribute_key': '/cron/proxyserver/distributekey',

    'receive_push_notifications': '/receive',
    'sync_top_level_path': '/sync',
    'notification_channels_list': '/sync/channels',
    'notifications_list': '/sync/notifications',
    'watch_for_user_deletion': '/sync/delete',
    'unsubscribe_from_notifications': '/sync/unsubscribe',

    'logout': '/logout',
}

