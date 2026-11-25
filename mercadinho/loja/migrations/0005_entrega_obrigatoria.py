import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("loja", "0004_marketplace")]

    operations = [
        migrations.AlterField(
            model_name="itempedido",
            name="entrega",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="itens",
                to="loja.pedidovendedor",
            ),
        ),
    ]
