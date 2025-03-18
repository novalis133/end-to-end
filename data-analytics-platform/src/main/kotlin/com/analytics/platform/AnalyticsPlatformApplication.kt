package com.analytics.platform

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication

@SpringBootApplication
class AnalyticsPlatformApplication

fun main(args: Array<String>) {
    runApplication<AnalyticsPlatformApplication>(*args)
}