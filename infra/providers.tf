terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-trackance-aks-bootstrap"
    storage_account_name = "trackanceakstfstate"
    container_name       = "golden-thread"
    key                  = "golden-thread.tfstate"
    use_azuread_auth     = true
  }
}

provider "azurerm" {
  features {}
}