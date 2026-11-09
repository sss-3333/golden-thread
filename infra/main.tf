resource "azurerm_resource_group" "ai" {
  name     = "rg-golden-thread-ai"
  location = "uksouth"
}

resource "azurerm_cognitive_account" "ai" {
  name                  = "goldenthread-ai-reader"
  location              = azurerm_resource_group.ai.location
  resource_group_name   = azurerm_resource_group.ai.name
  kind                  = "OpenAI"
  sku_name              = "S0"
  custom_subdomain_name = "goldenthread-ai-reader"
}

resource "azurerm_cognitive_deployment" "extract" {
  name                   = "extract"
  cognitive_account_id   = azurerm_cognitive_account.ai.id
  version_upgrade_option = "NoAutoUpgrade"

  model {
    format  = "OpenAI"
    name    = "gpt-4.1-mini"
    version = "2025-04-14"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 100
  }
}