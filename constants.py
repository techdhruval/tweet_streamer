USE_SOCIAL_QUERY = 'use social'
LAST_SEVEN_DAYS_TOKEN_QUERY = 'SELECT symbol, name, created_at FROM social.uniswap_v2_pairs AS uvp WHERE FROM_UNIXTIME(uvp.created_at) > now() - INTERVAL 7 day ORDER BY created_at ASC'
