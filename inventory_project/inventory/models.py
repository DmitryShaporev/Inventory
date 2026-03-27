from django.db import models


class Izm(models.Model):
    title = models.CharField("Ед.изм",max_length=50, unique=True,blank=False,db_index=True)

    def __str__(self):
        return self.title

    class Meta:

        db_table = 'izm'
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'


class Category(models.Model):
    title = models.CharField('Категория',max_length=100,db_index=True,unique=True)

    def __str__(self):
        return self.title

    class Meta:

        db_table = 'category'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Nom(models.Model):
    title = models.CharField('Наименование',max_length=200, blank=False, null=True,db_index=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        verbose_name='Категория',


    )
    izm = models.ForeignKey(
        Izm,
        on_delete=models.PROTECT,  # Нельзя удалить единицу измерения, если есть товары с ней
        blank=True,
        null=True,
        verbose_name='Ед.изм.',

    )

    def __str__(self):
        return self.title or 'Без названия'

    class Meta:

        db_table = 'nom'
        verbose_name = 'Номенклатура'
        verbose_name_plural = 'Номенклатура'


class Podraz(models.Model):
    title = models.CharField('Подразделение',max_length=100, unique=True,blank=False,db_index=True)

    def __str__(self):
        return self.title

    class Meta:

        db_table = 'podraz'
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'


class Obct(models.Model):
    title = models.CharField('Объект',max_length=100,db_index=True,blank=True,null=True)
    idpodraz = models.ForeignKey(
        Podraz,
        on_delete=models.PROTECT,
        db_column='idpodraz',
        verbose_name='Подразделение'
    )

    def __str__(self):
        return self.title

    class Meta:

        db_table = 'obct'
        verbose_name = 'Объект'
        verbose_name_plural = 'Объекты'


class Postav(models.Model):
    title = models.CharField(max_length=100, unique=True,db_index=True)

    def __str__(self):
        return self.title

    class Meta:

        db_table = 'postav'
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class Fio(models.Model):
    title = models.CharField('Подотчетное лицо',max_length=100, unique=True,db_index=True)

    def __str__(self):
        return self.title

    class Meta:

        db_table = 'fio'
        verbose_name = 'Подотчетное лицо'
        verbose_name_plural = 'Подотчетные лица'


class Doc(models.Model):
    nomer = models.CharField('Номер', max_length=50, db_index=True)  # ← Добавил индекс

    postav = models.ForeignKey(
        Postav,
        on_delete=models.PROTECT,
        verbose_name='Поставщик',
        blank=True,
        null=True,
        db_index=True
    )
    obct = models.ForeignKey(
        Obct,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Объект',
        db_index=True
    )
    fio = models.ForeignKey(
        Fio,
        on_delete=models.PROTECT,
        verbose_name='Подотчет',
        blank=True,
        null=True,
        db_index=True
    )
    oper = models.IntegerField('Операция', db_index=True)
    update_date = models.DateTimeField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Итого')
    datadoc = models.DateField(db_index=True)

    def __str__(self):
        return f"Документ №{self.nomer} от {self.datadoc}"

    class Meta:
        db_table = 'doc'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        indexes = [
            models.Index(fields=['datadoc', 'oper']),  # Составной индекс для фильтрации
            models.Index(fields=['nomer']),
        ]


class Detail(models.Model):
    id_doc = models.ForeignKey(
        Doc,
        on_delete=models.PROTECT,
        db_column='id_doc',
        blank=True,
        null=True,
        related_name='details',
        db_index=True  # ← Добавил индекс
    )
    id_nom = models.ForeignKey(
        Nom,
        on_delete=models.PROTECT,
        db_column='id_nom',
        blank=True,
        null=True,
        verbose_name='Наименование',
        db_index=True  # ← Добавил индекс
    )
    kolvo = models.DecimalField('Количество', max_digits=12, decimal_places=4)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    cost = models.DecimalField('Стоимость', max_digits=10, decimal_places=2)
    oper = models.IntegerField('Тип документа', blank=True, null=True)

    vat_rate = models.DecimalField(
        'Ставка НДС, %',
        max_digits=5,
        decimal_places=2,
        default=22.00,
        help_text='Ставка НДС в процентах'
    )
    vat_amount = models.DecimalField(
        'Сумма НДС',
        max_digits=10,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
        help_text='Сумма НДС в рублях'
    )
    total_with_vat = models.DecimalField(
        'Сумма с НДС',
        max_digits=10,
        decimal_places=2,
        default=0.00,
        blank=True,
        null=True,
        help_text='Стоимость с учетом НДС'
    )

    def __str__(self):
        return f"{self.id_nom} - {self.kolvo} x {self.price}"

    class Meta:
        db_table = 'detail'
        verbose_name = 'Табличная часть документа'
        verbose_name_plural = 'Табличная часть документов'
        indexes = [
            models.Index(fields=['id_doc']),  # Для связей
            models.Index(fields=['id_nom']),  # Для поиска по товарам
        ]

class Spis(models.Model):
    title = models.CharField(max_length=100, unique=True,blank=False)

    def __str__(self):
        return self.title

    class Meta:

        db_table = 'spis'
        verbose_name = 'Списание'
        verbose_name_plural = 'Списания'


class Manage(models.Model):
    obkt=models.ForeignKey(
        Obct,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='Объект',
        db_index=True
    )


    fio = models.ForeignKey(
        Fio,
        on_delete=models.PROTECT,
        db_column='fio',
        verbose_name='Подотчетное лицо',
        blank=True,
        null=True
)


    class Meta:

        verbose_name = 'Управление складом'
        verbose_name_plural = 'Управление складом'

