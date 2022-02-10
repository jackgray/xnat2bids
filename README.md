Retrieve data from XNAT

auth:
    make_token
        encrypt
    decrypt
        make_alias
            encrypt
        decrypt
            get jsession token
                successful token/alias creation confirmed

download exam:
    auth()
        use jsession in cookies to request data from XNAT
            get mrsessions
                if _makedirs
                    fix perms
            download bids
                download
                    fix perms
                unzip
                    fix perms
            download gre 
                download
                    fix_perms
                unzip
                    fix perms
            organize
                fix perms