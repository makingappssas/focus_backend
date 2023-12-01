from django.urls import re_path
from block_chain.methods import blr,nft
urlpatterns=[
    re_path(r'BuyBlr$',blr.buy_blr),
    re_path(r'HistoryBlr$',blr.history_blr),
    re_path(r'BuyNft$',nft.buy_nft),
    re_path(r'HistoryNft$',nft.history_nft),
    # re_path(r'CreateNft$',nft.create_nft),
    # re_path(r'DeleteNft$',nft.delete_nft),
    # re_path(r'GetNft$',nft.get_nft),
    re_path(r'MyNfts$',nft.get_my_nfts),
    re_path(r'TokenId/(?P<param>\w+)$', nft.get_token_id),
    re_path(r'CantNftAvailable$',nft.get_cant_allow_nft),
    # re_path(r'create_bulk_nft$',nft.create_bulk_nft),

    re_path(r'HistoryReferralsEarnings$',nft.history_ref),
    ]