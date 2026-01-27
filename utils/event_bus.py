"""
Système d'événements pour les mises à jour en temps réel dans l'application
Permet aux différents écrans de s'abonner aux changements de données
"""

from typing import Callable, Dict, List, Any
from kivy.clock import Clock


class EventBus:
    """Bus d'événements centralisé pour l'application"""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._event_queue: List[tuple] = []
    
    def subscribe(self, event_type: str, callback: Callable, *args, **kwargs):
        """
        S'abonner à un type d'événement
        
        Args:
            event_type: Type d'événement ('budget_changed', 'transaction_added', etc.)
            callback: Fonction à appeler quand l'événement se produit
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        # Stocker avec les arguments
        self._listeners[event_type].append({
            'callback': callback,
            'args': args,
            'kwargs': kwargs
        })
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Se désabonner d'un type d'événement"""
        if event_type in self._listeners:
            self._listeners[event_type] = [
                listener for listener in self._listeners[event_type] 
                if listener['callback'] != callback
            ]
    
    def emit(self, event_type: str, data: Any = None, immediate: bool = False):
        """
        Émettre un événement
        
        Args:
            event_type: Type d'événement
            data: Données à passer aux listeners
            immediate: Si True, exécute immédiatement, sinon planifie pour le prochain frame
        """
        if immediate:
            self._process_event(event_type, data)
        else:
            # Planifier pour le prochain frame Kivy
            Clock.schedule_once(lambda dt: self._process_event(event_type, data))
    
    def _process_event(self, event_type: str, data: Any = None):
        """Traite un événement et notifie tous les listeners"""
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    # Appeler le callback avec les arguments stockés et les nouvelles données
                    listener['callback'](data, *listener['args'], **listener['kwargs'])
                except Exception as e:
                    print(f"Erreur lors du traitement de l'événement {event_type}: {e}")
    
    def clear_all(self):
        """Supprime tous les listeners"""
        self._listeners.clear()


# Instance globale du bus d'événements
event_bus = EventBus()


# Types d'événements disponibles
class EventTypes:
    BUDGET_CHANGED = "budget_changed"
    TRANSACTION_ADDED = "transaction_added"
    TRANSACTION_UPDATED = "transaction_updated"
    TRANSACTION_DELETED = "transaction_deleted"
    DATA_RESET = "data_reset"
    USER_CHANGED = "user_changed"
    CATEGORY_CHANGED = "category_changed"
    ACCOUNT_CHANGED = "account_changed"


# Fonctions utilitaires pour faciliter l'utilisation
def notify_budget_changed(new_budget: int = None, account_id: int = None):
    """Notifie que le budget a changé"""
    event_bus.emit(EventTypes.BUDGET_CHANGED, {
        'budget': new_budget,
        'account_id': account_id
    })


def notify_transaction_added(transaction_data: dict = None):
    """Notifie qu'une transaction a été ajoutée"""
    event_bus.emit(EventTypes.TRANSACTION_ADDED, transaction_data)


def notify_transaction_deleted(transaction_id: int = None):
    """Notifie qu'une transaction a été supprimée"""
    event_bus.emit(EventTypes.TRANSACTION_DELETED, {
        'transaction_id': transaction_id
    })


def notify_data_reset():
    """Notifie que les données ont été réinitialisées"""
    event_bus.emit(EventTypes.DATA_RESET)


def notify_user_changed():
    """Notifie que les informations utilisateur ont changé"""
    event_bus.emit(EventTypes.USER_CHANGED)


def subscribe_to_data_changes(callback: Callable):
    """S'abonne à tous les changements de données"""
    event_bus.subscribe(EventTypes.BUDGET_CHANGED, callback)
    event_bus.subscribe(EventTypes.TRANSACTION_ADDED, callback)
    event_bus.subscribe(EventTypes.TRANSACTION_DELETED, callback)
    event_bus.subscribe(EventTypes.DATA_RESET, callback)
