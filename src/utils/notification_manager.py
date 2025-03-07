import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import requests
from pathlib import Path
from .user_input import cargar_configuracion

class NotificationManager:
    def __init__(self):
        self.config = self._cargar_config_notificaciones()
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'email': os.getenv('NOTIFICATION_EMAIL'),
            'password': os.getenv('NOTIFICATION_EMAIL_PASSWORD')
        }

    def enviar_notificacion(self, titulo: str, mensaje: str, tipo: str = 'info') -> bool:
        """Envía una notificación por los canales configurados"""
        try:
            # Registrar en log
            log_level = logging.ERROR if tipo == 'error' else logging.INFO
            logging.log(log_level, f"{titulo}: {mensaje}")

            # Enviar por email si está configurado
            if all(self.email_config.values()):
                self._enviar_email(titulo, mensaje)

            # Enviar a Slack si está configurado
            if self.slack_webhook:
                self._enviar_slack(titulo, mensaje)

            return True

        except Exception as e:
            logging.error(f"Error al enviar notificación: {str(e)}")
            return False

    def _enviar_email(self, titulo: str, mensaje: str):
        """Envía notificación por email"""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"WebGenesis - {titulo}"
            msg['From'] = self.email_config['email']
            msg['To'] = self.email_config['email']
            msg.attach(MIMEText(mensaje, 'plain'))

            with smtplib.SMTP(
                self.email_config['smtp_server'],
                self.email_config['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.email_config['email'],
                    self.email_config['password']
                )
                server.send_message(msg)

        except Exception as e:
            logging.error(f"Error al enviar email: {str(e)}")

    def _enviar_slack(self, titulo: str, mensaje: str):
        """Envía notificación a Slack"""
        try:
            payload = {
                "text": f"*{titulo}*\n{mensaje}"
            }
            requests.post(self.slack_webhook, json=payload)

        except Exception as e:
            logging.error(f"Error al enviar a Slack: {str(e)}")

    def _cargar_config_notificaciones(self) -> dict:
        """Carga la configuración de notificaciones"""
        try:
            config = cargar_configuracion()
            return config.get('notifications', {})
        except:
            return {}

    def notificar_error_critico(self, error: str, detalles: Optional[str] = None):
        """Envía notificación de error crítico"""
        mensaje = f"ERROR CRÍTICO: {error}"
        if detalles:
            mensaje += f"\n\nDetalles:\n{detalles}"
        
        self.enviar_notificacion(
            "Error Crítico Detectado",
            mensaje,
            tipo='error'
        )
