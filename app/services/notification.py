# app/services/notification.py
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    BOOKING_CREATED = "booking_created"
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_REMINDER = "booking_reminder"
    BOOKING_COMPLETED = "booking_completed"
    REVIEW_REQUEST = "review_request"
    PASSWORD_RESET = "password_reset"
    WELCOME = "welcome"


@dataclass
class NotificationTemplate:
    subject: str
    html_body: str
    text_body: str


class NotificationService:
    def __init__(self, smtp_config: Dict = None):
        self.smtp_config = smtp_config or {
            'host': 'localhost',
            'port': 587,
            'username': '',
            'password': '',
            'use_tls': True
        }
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[NotificationType, NotificationTemplate]:
        """Carrega templates de email para diferentes tipos de notificação"""
        return {
            NotificationType.BOOKING_CREATED: NotificationTemplate(
                subject="Agendamento criado - CarWash",
                html_body="""
                <h2>Agendamento Criado com Sucesso!</h2>
                <p>Olá {user_name},</p>
                <p>Seu agendamento foi criado com sucesso:</p>
                <ul>
                    <li><strong>Lava-jato:</strong> {car_wash_name}</li>
                    <li><strong>Serviço:</strong> {service_name}</li>
                    <li><strong>Data:</strong> {booking_date}</li>
                    <li><strong>Horário:</strong> {booking_time}</li>
                    <li><strong>Valor:</strong> R$ {service_price}</li>
                </ul>
                <p>Aguarde a confirmação do lava-jato.</p>
                <p>Obrigado por usar o CarWash!</p>
                """,
                text_body="""
                Agendamento Criado com Sucesso!

                Olá {user_name},

                Seu agendamento foi criado com sucesso:
                - Lava-jato: {car_wash_name}
                - Serviço: {service_name}
                - Data: {booking_date}
                - Horário: {booking_time}
                - Valor: R$ {service_price}

                Aguarde a confirmação do lava-jato.

                Obrigado por usar o CarWash!
                """
            ),

            NotificationType.BOOKING_CONFIRMED: NotificationTemplate(
                subject="Agendamento confirmado - CarWash",
                html_body="""
                <h2>Agendamento Confirmado!</h2>
                <p>Olá {user_name},</p>
                <p>Seu agendamento foi <strong>confirmado</strong>:</p>
                <ul>
                    <li><strong>Lava-jato:</strong> {car_wash_name}</li>
                    <li><strong>Serviço:</strong> {service_name}</li>
                    <li><strong>Data:</strong> {booking_date}</li>
                    <li><strong>Horário:</strong> {booking_time}</li>
                </ul>
                <p><strong>Endereço:</strong> {car_wash_address}</p>
                <p><strong>Telefone:</strong> {car_wash_phone}</p>
                <p>Nos vemos lá!</p>
                """,
                text_body="""
                Agendamento Confirmado!

                Olá {user_name},

                Seu agendamento foi confirmado:
                - Lava-jato: {car_wash_name}
                - Serviço: {service_name}
                - Data: {booking_date}
                - Horário: {booking_time}

                Endereço: {car_wash_address}
                Telefone: {car_wash_phone}

                Nos vemos lá!
                """
            ),

            NotificationType.BOOKING_REMINDER: NotificationTemplate(
                subject="Lembrete: Seu agendamento é amanhã - CarWash",
                html_body="""
                <h2>Lembrete de Agendamento</h2>
                <p>Olá {user_name},</p>
                <p>Este é um lembrete de que você tem um agendamento <strong>amanhã</strong>:</p>
                <ul>
                    <li><strong>Lava-jato:</strong> {car_wash_name}</li>
                    <li><strong>Serviço:</strong> {service_name}</li>
                    <li><strong>Data:</strong> {booking_date}</li>
                    <li><strong>Horário:</strong> {booking_time}</li>
                </ul>
                <p><strong>Endereço:</strong> {car_wash_address}</p>
                <p>Não se esqueça!</p>
                """,
                text_body="""
                Lembrete de Agendamento

                Olá {user_name},

                Este é um lembrete de que você tem um agendamento amanhã:
                - Lava-jato: {car_wash_name}
                - Serviço: {service_name}
                - Data: {booking_date}
                - Horário: {booking_time}

                Endereço: {car_wash_address}

                Não se esqueça!
                """
            ),

            NotificationType.REVIEW_REQUEST: NotificationTemplate(
                subject="Avalie seu atendimento - CarWash",
                html_body="""
                <h2>Como foi seu atendimento?</h2>
                <p>Olá {user_name},</p>
                <p>Esperamos que tenha gostado do serviço no <strong>{car_wash_name}</strong>!</p>
                <p>Sua opinião é muito importante para nós. Que tal avaliar o atendimento?</p>
                <p>Leva apenas alguns segundos e ajuda outros usuários.</p>
                <p><a href="{review_link}">Avaliar agora</a></p>
                <p>Obrigado!</p>
                """,
                text_body="""
                Como foi seu atendimento?

                Olá {user_name},

                Esperamos que tenha gostado do serviço no {car_wash_name}!

                Sua opinião é muito importante para nós. Que tal avaliar o atendimento?

                Acesse: {review_link}

                Obrigado!
                """
            ),

            NotificationType.PASSWORD_RESET: NotificationTemplate(
                subject="Redefinir senha - CarWash",
                html_body="""
                <h2>Redefinir Senha</h2>
                <p>Olá,</p>
                <p>Você solicitou a redefinição de sua senha no CarWash.</p>
                <p>Clique no link abaixo para criar uma nova senha:</p>
                <p><a href="{reset_link}">Redefinir Senha</a></p>
                <p>Este link expira em 1 hora.</p>
                <p>Se você não solicitou esta alteração, ignore este email.</p>
                """,
                text_body="""
                Redefinir Senha

                Olá,

                Você solicitou a redefinição de sua senha no CarWash.

                Acesse o link abaixo para criar uma nova senha:
                {reset_link}

                Este link expira em 1 hora.

                Se você não solicitou esta alteração, ignore este email.
                """
            ),

            NotificationType.WELCOME: NotificationTemplate(
                subject="Bem-vindo ao CarWash!",
                html_body="""
                <h2>Bem-vindo ao CarWash!</h2>
                <p>Olá {user_name},</p>
                <p>Seja bem-vindo à nossa plataforma!</p>
                <p>Agora você pode:</p>
                <ul>
                    <li>Encontrar lava-jatos próximos</li>
                    <li>Agendar serviços facilmente</li>
                    <li>Avaliar e ver avaliações</li>
                    <li>Acompanhar seus agendamentos</li>
                </ul>
                <p>Aproveite e faça seu primeiro agendamento!</p>
                """,
                text_body="""
                Bem-vindo ao CarWash!

                Olá {user_name},

                Seja bem-vindo à nossa plataforma!

                Agora você pode:
                - Encontrar lava-jatos próximos
                - Agendar serviços facilmente
                - Avaliar e ver avaliações
                - Acompanhar seus agendamentos

                Aproveite e faça seu primeiro agendamento!
                """
            )
        }

    def send_email(self, to_email: str, notification_type: NotificationType, data: Dict) -> bool:
        """Envia email usando template específico"""
        try:
            template = self.templates.get(notification_type)
            if not template:
                logger.error(f"Template não encontrado para: {notification_type}")
                return False

            # Formata o conteúdo com os dados
            subject = template.subject.format(**data)
            html_body = template.html_body.format(**data)
            text_body = template.text_body.format(**data)

            # Cria mensagem
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_config.get('username', 'noreply@carwash.com')
            msg['To'] = to_email

            # Adiciona conteúdo
            msg.attach(MimeText(text_body, 'plain', 'utf-8'))
            msg.attach(MimeText(html_body, 'html', 'utf-8'))

            # Envia email
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                if self.smtp_config.get('use_tls'):
                    server.starttls()

                if self.smtp_config.get('username') and self.smtp_config.get('password'):
                    server.login(self.smtp_config['username'], self.smtp_config['password'])

                server.send_message(msg)

            logger.info(f"Email enviado para {to_email}: {notification_type}")
            return True

        except Exception as e:
            logger.error(f"Erro ao enviar email para {to_email}: {str(e)}")
            return False

    def send_booking_created(self, user_email: str, user_name: str, booking_data: Dict) -> bool:
        """Envia notificação de agendamento criado"""
        return self.send_email(
            user_email,
            NotificationType.BOOKING_CREATED,
            {
                'user_name': user_name,
                **booking_data
            }
        )

    def send_booking_confirmed(self, user_email: str, user_name: str, booking_data: Dict) -> bool:
        """Envia notificação de agendamento confirmado"""
        return self.send_email(
            user_email,
            NotificationType.BOOKING_CONFIRMED,
            {
                'user_name': user_name,
                **booking_data
            }
        )

    def send_booking_reminder(self, user_email: str, user_name: str, booking_data: Dict) -> bool:
        """Envia lembrete de agendamento"""
        return self.send_email(
            user_email,
            NotificationType.BOOKING_REMINDER,
            {
                'user_name': user_name,
                **booking_data
            }
        )

    def send_review_request(self, user_email: str, user_name: str, booking_data: Dict) -> bool:
        """Envia solicitação de avaliação"""
        return self.send_email(
            user_email,
            NotificationType.REVIEW_REQUEST,
            {
                'user_name': user_name,
                'review_link': f"https://app.carwash.com/review/{booking_data.get('booking_id')}",
                **booking_data
            }
        )

    def send_password_reset(self, user_email: str, reset_token: str) -> bool:
        """Envia email de redefinição de senha"""
        return self.send_email(
            user_email,
            NotificationType.PASSWORD_RESET,
            {
                'reset_link': f"https://app.carwash.com/reset-password?token={reset_token}"
            }
        )

    def send_welcome(self, user_email: str, user_name: str) -> bool:
        """Envia email de boas-vindas"""
        return self.send_email(
            user_email,
            NotificationType.WELCOME,
            {
                'user_name': user_name
            }
        )

    def send_bulk_reminders(self, reminders: List[Dict]) -> int:
        """Envia lembretes em lote"""
        sent_count = 0
        for reminder in reminders:
            if self.send_booking_reminder(
                    reminder['user_email'],
                    reminder['user_name'],
                    reminder['booking_data']
            ):
                sent_count += 1

        logger.info(f"Lembretes enviados: {sent_count}/{len(reminders)}")
        return sent_count


# Instância global do serviço
notification_service = NotificationService()


# Funções de conveniência
def send_booking_created_notification(user_email: str, user_name: str, booking_data: Dict) -> bool:
    return notification_service.send_booking_created(user_email, user_name, booking_data)


def send_booking_confirmed_notification(user_email: str, user_name: str, booking_data: Dict) -> bool:
    return notification_service.send_booking_confirmed(user_email, user_name, booking_data)


def send_booking_reminder_notification(user_email: str, user_name: str, booking_data: Dict) -> bool:
    return notification_service.send_booking_reminder(user_email, user_name, booking_data)


def send_review_request_notification(user_email: str, user_name: str, booking_data: Dict) -> bool:
    return notification_service.send_review_request(user_email, user_name, booking_data)


def send_password_reset_notification(user_email: str, reset_token: str) -> bool:
    return notification_service.send_password_reset(user_email, reset_token)


def send_welcome_notification(user_email: str, user_name: str) -> bool:
    return notification_service.send_welcome(user_email, user_name)