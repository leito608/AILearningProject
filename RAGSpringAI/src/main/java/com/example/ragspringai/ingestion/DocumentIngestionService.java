package com.example.ragspringai.ingestion;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.reader.tika.TikaDocumentReader;
import org.springframework.ai.transformer.splitter.TextSplitter;
import org.springframework.ai.transformer.splitter.TokenTextSplitter;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.Resource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DocumentIngestionService implements CommandLineRunner {
    private static final Logger logger = LoggerFactory.getLogger(DocumentIngestionService.class);
    private static final int BATCH_SIZE = 10;

    @Value("classpath:/pdf/spring-boot-reference.pdf")
    private Resource pdfResource;

    private final VectorStore vectorStore;
    private final JdbcTemplate jdbcTemplate;

    public DocumentIngestionService(VectorStore vectorStore, JdbcTemplate jdbcTemplate) {
        this.vectorStore = vectorStore;
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public void run(String... args) throws Exception {
        String fileName = pdfResource.getFilename();

        if (alreadyIngested(fileName)) {
            logger.info("'{}' is already ingested, skipping", fileName);
            return;
        }

        logger.info("Ingesting '{}'", fileName);
        TikaDocumentReader reader = new TikaDocumentReader(pdfResource);
        TextSplitter splitter = TokenTextSplitter.builder().build();
        List<Document> chunks = splitter.split(reader.read());
        logger.info("Total chunks: {}", chunks.size());

        for (int i = 0; i < chunks.size(); i += BATCH_SIZE) {
            int end = Math.min(i + BATCH_SIZE, chunks.size());
            vectorStore.accept(chunks.subList(i, end));
            logger.info("Stored {}/{}", end, chunks.size());
        }

        logger.info("Ingestion complete");
    }

    private boolean alreadyIngested(String fileName) {
        Integer count = jdbcTemplate.queryForObject(
                "SELECT count(*) FROM vector_store WHERE metadata->>'source' = ?",
                Integer.class,
                fileName);
        return count != null && count > 0;
    }
}