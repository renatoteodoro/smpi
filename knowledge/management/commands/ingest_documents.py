"""
Ingest PDF/DOCX/TXT files into KnowledgeDocument + DocumentChunk with embeddings.

Usage:
    python manage.py ingest_documents --dir data/
    python manage.py ingest_documents --file data/Doc1.pdf --fault-code cocked_rotor_2
    python manage.py ingest_documents --all   # re-ingest all non-ingested docs
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Ingest documents into the knowledge base (RAG).'

    def add_arguments(self, parser):
        parser.add_argument('--dir', help='Directory containing documents to ingest')
        parser.add_argument('--file', help='Single file to ingest')
        parser.add_argument('--fault-code', help='Associate documents with this fault code')
        parser.add_argument('--all', action='store_true', help='Re-ingest all KnowledgeDocuments')

    def handle(self, *args, **options):
        from django.core.files import File

        from faults.models import Fault
        from knowledge.ingest import ingest_document
        from knowledge.models import KnowledgeDocument

        fault = None
        if options.get('fault_code'):
            try:
                fault = Fault.objects.get(code=options['fault_code'])
            except Fault.DoesNotExist:
                raise CommandError(f"Fault '{options['fault_code']}' not found.")

        docs_to_ingest = []

        if options.get('all'):
            docs_to_ingest = list(
                KnowledgeDocument.objects.filter(file__isnull=False).exclude(file='')
            )
            self.stdout.write(f'Re-ingesting {len(docs_to_ingest)} existing documents...')

        elif options.get('dir'):
            dir_path = Path(options['dir'])
            if not dir_path.exists():
                raise CommandError(f'Directory not found: {dir_path}')
            suffixes = {'.pdf', '.docx', '.txt'}
            files = [f for f in sorted(dir_path.iterdir()) if f.suffix.lower() in suffixes]
            self.stdout.write(f'Found {len(files)} document(s) in {dir_path}')

            for f in files:
                doc, created = KnowledgeDocument.objects.get_or_create(
                    title=f.stem,
                    defaults={
                        'description': f'Importado de {f.name}',
                        'fault': fault,
                        'tags': '',
                    }
                )
                with open(f, 'rb') as fh:
                    doc.file.save(f.name, File(fh), save=True)
                docs_to_ingest.append(doc)

        elif options.get('file'):
            file_path = Path(options['file'])
            if not file_path.exists():
                raise CommandError(f'File not found: {file_path}')
            doc, created = KnowledgeDocument.objects.get_or_create(
                title=file_path.stem,
                defaults={
                    'fault': fault,
                    'description': f'Importado de {file_path.name}',
                },
            )
            with open(file_path, 'rb') as fh:
                doc.file.save(file_path.name, File(fh), save=True)
            docs_to_ingest.append(doc)

        else:
            raise CommandError('Provide --dir, --file, or --all.')

        total_chunks = 0
        for doc in docs_to_ingest:
            self.stdout.write(f'  Ingesting: {doc.title}...')
            try:
                count = ingest_document(doc)
                total_chunks += count
                self.stdout.write(self.style.SUCCESS(f'    -> {count} chunks'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    -> ERROR: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {len(docs_to_ingest)} documents, {total_chunks} total chunks.'
        ))
