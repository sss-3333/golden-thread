locals {
  compare_models = {
    "gpt-4.1"      = "2025-04-14"
    "gpt-4.1-nano" = "2025-04-14"
  }
}

resource "azurerm_cognitive_deployment" "compare" {
  for_each               = local.compare_models
  name                   = each.key
  cognitive_account_id   = azurerm_cognitive_account.ai.id
  version_upgrade_option = "NoAutoUpgrade"

  model {
    format  = "OpenAI"
    name    = each.key
    version = each.value
  }

  sku {
    name     = "GlobalStandard"
    capacity = 50
  }
}