kind_mapping = {
    'Cash': ['SPAXX**','FZDXX'],
    'IndexFund': ['FXAIX','VOO','QQQ'],
}
m = {
        s:k
        for k,l in kind_mapping.items()
        for s in l
}

print(m)