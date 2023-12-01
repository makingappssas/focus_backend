from django.urls import re_path
from services.methods import authentication, pqrs, academy, referrals, notifications
urlpatterns=[
    ##AUTHENTICATION##
    re_path(r'Register$',authentication.registration), 
    re_path(r'Login$',authentication.login),   
    re_path(r'GetCode$',authentication.get_code),  
    re_path(r'ChangePassword$',authentication.change_password), 
    re_path(r'ChangeCode$',authentication.change_code_mail), 
    re_path(r'LogOut$',authentication.log_out), 
    re_path(r'languageUpdate$',authentication.language_update), 
    re_path(r'GetAllUsers',authentication.get_users),
    re_path(r'create_sp_admin',authentication.create_sp_admin),
    ######################PQRS######################
    re_path(r'ListCategory$',pqrs.ListCategory),
    re_path(r'CreateTicket$',pqrs.CreateTicket),
    re_path(r'TicketsFilter$',pqrs.TicketsFilter),
    re_path(r'Chat$',pqrs.Chat),
    re_path(r'ListStatus$',pqrs.ListStatus),
    re_path(r'FinishedTickets$',pqrs.FinishedTickets),
    ########################ACADEMY########################
    re_path(r'SaveChapter',academy.save_chapter),
    re_path(r'GeTypesDocument',academy.get_type_document_get),
    re_path(r'GetFilesAcademy',academy.get_files_academy),
    re_path(r'GetCurses',academy.get_curses),
    re_path(r'EditFileAcademy',academy.edit_file_academy),
    re_path(r'DeleteAcademy',academy.delete_academy),
    re_path(r'DeleteCourseVideo',academy.delete_course_video),
    re_path(r'EditCourseVideo',academy.edit_course_video),
    re_path(r'GetOnlyOneFile',academy.get_only_one_file),
    re_path(r'GetOnlyOneVideo',academy.get_only_video),
    re_path(r'GetTypesAndProfiles',academy.get_type_file),
    
    re_path(r'GetReferrals',referrals.get_referrals),
    re_path(r'PostWallet',referrals.post_wallet),
    re_path(r'SpWallet',referrals.wallet_sp),
    re_path(r'PostConnection',referrals.post_wallet_connection),
    re_path(r'ListReferrals',referrals.get_referrals_list),
    re_path(r'GetCantUsers',referrals.get_users_cant),
    re_path(r'AmountOfRef',referrals.amount_ref),
    
    
    ####################Notifications#########################3
    re_path(r"NotificationCreate$",notifications.notification),
    re_path(r"CantNotifications$",notifications.cant_notications),
    # re_path(r"GetUsersNotifications$",notifications.get_user_notification),
    re_path(r"NotificationsGet$",notifications.notification_get),
    re_path(r"NotifyDelate$",notifications.notification_delete),
]