FROM odoo:18

COPY ./odoo.conf /etc/odoo/odoo.conf

CMD ["odoo", "--db_host=postgres.railway.internal", "--db_port=5432", "--db_user=postgres", "--db_password=الباسورد_الحقيقي", "-c", "/etc/odoo/odoo.conf"]