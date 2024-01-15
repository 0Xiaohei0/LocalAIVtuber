
def pluginToNameMap(pluginList):
    ProviderList = []  # Plugin names for display in UI
    ProviderMap = {}  # Map plugin names to instances
    for provider in pluginList:
        provider_name = provider.__class__.__name__
        ProviderList.append(provider_name)
        ProviderMap[provider_name] = provider
    return ProviderList, ProviderMap
