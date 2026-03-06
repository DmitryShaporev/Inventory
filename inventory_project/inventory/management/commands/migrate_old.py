from django.core.management.base import BaseCommand
from django.db import connections
from ...models import (
    Izm, Category, Nom, Podraz, Obct, Postav, Fio, Doc, Detail, Spis
)
from datetime import datetime
import re


class Command(BaseCommand):
    help = 'Перенос данных из старой БД warehouse.db в новую структуру'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Пробный запуск без сохранения в БД',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']

        if self.dry_run:
            self.stdout.write(self.style.WARNING('ПРОБНЫЙ ЗАПУСК (данные НЕ сохраняются)'))

        self.stdout.write('Начинаем перенос данных...')

        # Проверяем подключение к старой БД
        try:
            cursor = connections['old'].cursor()
            self.stdout.write(self.style.SUCCESS('Подключение к warehouse.db установлено'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка подключения к warehouse.db: {e}'))
            self.stdout.write('Проверь настройки DATABASES в settings.py')
            return

        # Переносим данные последовательно
        self.migrate_izm(cursor)
        self.migrate_category(cursor)
        self.migrate_podraz(cursor)
        self.migrate_postav(cursor)
        self.migrate_fio(cursor)
        self.migrate_spis(cursor)
        self.migrate_obct(cursor)
        self.migrate_nom(cursor)
        self.migrate_doc(cursor)
        self.migrate_detail(cursor)

        self.stdout.write(self.style.SUCCESS('Перенос успешно завершен!'))

    def migrate_izm(self, cursor):
        self.stdout.write('Перенос единиц измерения...')
        try:
            cursor.execute("SELECT id, title FROM izm")
            rows = cursor.fetchall()
            for row in rows:
                if not self.dry_run:
                    Izm.objects.get_or_create(
                        id=row[0],
                        defaults={'title': row[1]}
                    )
            self.stdout.write(f'  ➡ Перенесено {len(rows)} записей')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_category(self, cursor):
        self.stdout.write('Перенос категорий...')
        try:
            cursor.execute("SELECT id, title FROM category")
            rows = cursor.fetchall()
            for row in rows:
                if not self.dry_run:
                    Category.objects.get_or_create(
                        id=row[0],
                        defaults={'title': row[1]}
                    )
            self.stdout.write(f'  ➡ Перенесено {len(rows)} записей')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_podraz(self, cursor):
        self.stdout.write('Перенос подразделений...')
        try:
            cursor.execute("SELECT id, title FROM podraz")
            rows = cursor.fetchall()
            for row in rows:
                if not self.dry_run:
                    Podraz.objects.get_or_create(
                        id=row[0],
                        defaults={'title': row[1]}
                    )
            self.stdout.write(f'  ➡ Перенесено {len(rows)} записей')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_postav(self, cursor):
        self.stdout.write('Перенос поставщиков...')
        try:
            cursor.execute("SELECT id, title FROM postav")
            rows = cursor.fetchall()
            for row in rows:
                if not self.dry_run:
                    Postav.objects.get_or_create(
                        id=row[0],
                        defaults={'title': row[1]}
                    )
            self.stdout.write(f'  ➡ Перенесено {len(rows)} записей')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_fio(self, cursor):
        self.stdout.write('Перенос подотчетных лиц...')
        try:
            cursor.execute("SELECT id, title FROM fio")
            rows = cursor.fetchall()
            for row in rows:
                if not self.dry_run:
                    Fio.objects.get_or_create(
                        id=row[0],
                        defaults={'title': row[1]}
                    )
            self.stdout.write(f'  ➡ Перенесено {len(rows)} записей')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_spis(self, cursor):
        self.stdout.write('Перенос причин списания...')
        try:
            cursor.execute("SELECT id, title FROM spis")
            rows = cursor.fetchall()
            for row in rows:
                if not self.dry_run:
                    Spis.objects.get_or_create(
                        id=row[0],
                        defaults={'title': row[1]}
                    )
            self.stdout.write(f'  ➡ Перенесено {len(rows)} записей')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_obct(self, cursor):
        self.stdout.write('Перенос объектов...')
        try:
            cursor.execute("SELECT id, title, idpodraz FROM obct")
            rows = cursor.fetchall()
            success = 0
            errors = 0

            for row in rows:
                try:
                    if not self.dry_run:
                        idpodraz = row[2] if row[2] else None
                        Obct.objects.get_or_create(
                            id=row[0],
                            defaults={
                                'title': row[1],
                                'idpodraz_id': idpodraz
                            }
                        )
                    success += 1
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.WARNING(f'    ⚠ Объект id={row[0]}: {e}'))

            self.stdout.write(f'  ➡ Успешно: {success}, Пропущено: {errors}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_nom(self, cursor):
        self.stdout.write('Перенос номенклатуры...')
        try:
            cursor.execute("SELECT id, title, category_id, izm_id FROM nom")
            rows = cursor.fetchall()
            success = 0
            errors = 0

            for row in rows:
                try:
                    if not self.dry_run:
                        Nom.objects.get_or_create(
                            id=row[0],
                            defaults={
                                'title': row[1],
                                'category_id': row[2],
                                'izm_id': row[3]
                            }
                        )
                    success += 1
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.WARNING(f'    ⚠ Номенклатура id={row[0]}: {e}'))

            self.stdout.write(f'  ➡ Успешно: {success}, Пропущено: {errors}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_doc(self, cursor):
        self.stdout.write('Перенос документов...')
        try:
            cursor.execute("""
                SELECT id, nomer, postav_id, obct_id, fio_id, 
                       oper, update_date, total, datadoc 
                FROM doc
            """)
            rows = cursor.fetchall()
            success = 0
            errors = 0

            for row in rows:
                try:
                    date_obj = self.parse_date(row[8]) if row[8] else None

                    if not self.dry_run:
                        Doc.objects.get_or_create(
                            id=row[0],
                            defaults={
                                'nomer': row[1],
                                'postav_id': row[2],
                                'obct_id': row[3],
                                'fio_id': row[4],
                                'oper': row[5],
                                'update_date': row[6],
                                'total': row[7],
                                'datadoc': date_obj
                            }
                        )
                    success += 1
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.WARNING(f'    ⚠ Документ id={row[0]}: {e}'))

            self.stdout.write(f'  ➡ Успешно: {success}, Ошибок: {errors}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def migrate_detail(self, cursor):
        self.stdout.write('Перенос деталей документов...')
        try:
            cursor.execute("""
                SELECT id, id_doc, id_nom, kolvo, price, cost, oper 
                FROM detail
            """)
            rows = cursor.fetchall()
            success = 0
            errors = 0

            self.stdout.write(f'  Найдено записей в старой БД: {len(rows)}')

            # Проверим, сколько уже есть в новой БД
            from ...models import Detail

            existing_count = Detail.objects.count()
            self.stdout.write(f'  Существующих записей в новой БД: {existing_count}')

            for row in rows:
                try:
                    # Проверяем, существует ли уже такая деталь
                    if Detail.objects.filter(id=row[0]).exists():
                        self.stdout.write(f'    ⚠ Деталь id={row[0]} уже существует, пропускаем')
                        continue

                    if not self.dry_run:
                        # Проверяем, существуют ли связанные записи
                        doc_exists = Doc.objects.filter(id=row[1]).exists()
                        nom_exists = Nom.objects.filter(id=row[2]).exists()

                        if not doc_exists:
                            self.stdout.write(
                                self.style.WARNING(f'    ⚠ Документ {row[1]} не найден для детали {row[0]}'))
                            errors += 1
                            continue

                        if not nom_exists:
                            self.stdout.write(
                                self.style.WARNING(f'    ⚠ Номенклатура {row[2]} не найдена для детали {row[0]}'))
                            errors += 1
                            continue

                        Detail.objects.create(
                            id=row[0],
                            id_doc_id=row[1],
                            id_nom_id=row[2],
                            kolvo=row[3],
                            price=row[4],
                            cost=row[5],
                            oper=row[6]
                        )
                    success += 1

                    # Прогресс каждые 1000 записей
                    if success % 1000 == 0:
                        self.stdout.write(f'    ...обработано {success} записей')

                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f'    ❌ Деталь id={row[0]}: {e}'))

            self.stdout.write(f'  ➡ Успешно: {success}, Ошибок: {errors}')

            # Финальная проверка
            if not self.dry_run:
                final_count = Detail.objects.count()
                self.stdout.write(f'  ➡ Всего в новой БД после переноса: {final_count}')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Ошибка: {e}'))

    def parse_date(self, date_str):
        """Парсит дату из формата DD.MM.YYYY в объект date"""
        if not date_str:
            return None

        date_str = str(date_str).strip()

        # Формат DD.MM.YYYY
        if re.match(r'\d{2}\.\d{2}\.\d{4}', date_str):
            try:
                return datetime.strptime(date_str, '%d.%m.%Y').date()
            except ValueError:
                pass

        # Формат YYYY-MM-DD
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        self.stdout.write(self.style.WARNING(f'  ⚠ Неизвестный формат даты: {date_str}'))
        return None