FROM odoo:18

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /mnt/extra-addons && chown -R odoo:odoo /mnt/extra-addons

COPY ./odoo_prod.conf /etc/odoo/odoo.conf
RUN chown odoo:odoo /etc/odoo/odoo.conf

COPY ./odoo/addons /mnt/extra-addons
RUN chown -R odoo:odoo /mnt/extra-addons

USER odoo

CMD ["odoo"]