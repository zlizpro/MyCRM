"""
MiniCRM 数据库性能测试

测试数据库查询性能、索引效果、缓存命中率等关键性能指标。
包含基准测试、性能回归检测和详细的性能报告。
"""

import logging
import tempfile
import time
import unittest
from pathlib import Path

from src.minicrm.core.database_performance_analyzer import (
    DatabasePerformanceAnalyzer,
)
from src.minicrm.core.performance_monitor import performance_monitor
from src.minicrm.data.database.database_manager import DatabaseManager


class DatabasePerformanceTest(unittest.TestCase):
    """数据库性能测试类"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.logger = logging.getLogger(__name__)
        cls.test_db_path = None
        cls.db_manager = None
        cls.analyzer = None

        # 性能基准值（毫秒）
        cls.PERFORMANCE_BENCHMARKS = {
            "simple_select": 10.0,  # 简单查询应在10ms内完成
            "complex_join": 50.0,  # 复杂连接查询应在50ms内完成
            "insert_single": 5.0,  # 单条插入应在5ms内完成
            "insert_batch": 100.0,  # 批量插入应在100ms内完成
            "update_single": 10.0,  # 单条更新应在10ms内完成
            "delete_single": 5.0,  # 单条删除应在5ms内完成
            "index_scan": 20.0,  # 索引扫描应在20ms内完成
            "full_table_scan": 200.0,  # 全表扫描应在200ms内完成
        }

        # 数据量基准
        cls.TEST_DATA_SIZES = {
            "small": 100,  # 小数据集
            "medium": 1000,  # 中等数据集
            "large": 10000,  # 大数据集
        }

    def setUp(self):
        """每个测试方法的初始化"""
        # 创建临时数据库
        self.test_db_path = tempfile.mktemp(suffix=".db")
        self.db_manager = DatabaseManager(self.test_db_path)

        # 创建性能分析器实例
        self.analyzer = DatabasePerformanceAnalyzer(slow_query_threshold=50.0)
        self.analyzer.enable()

        # 清空性能监控数据
        performance_monitor.clear_metrics()
        self.analyzer.clear_metrics()

        # 创建测试表结构
        self._create_test_tables()

        # 插入测试数据
        self._insert_test_data()

        self.logger.info(f"数据库性能测试初始化完成: {self.test_db_path}")

    def tearDown(self):
        """每个测试方法的清理"""
        try:
            if self.db_manager:
                self.db_manager.close()

            if self.test_db_path and Path(self.test_db_path).exists():
                Path(self.test_db_path).unlink()

            self.logger.info("数据库性能测试清理完成")

        except Exception as e:
            self.logger.error(f"测试清理失败: {e}")

    def test_simple_select_performance(self):
        """测试简单查询性能"""
        self.logger.info("开始测试简单查询性能")

        # 执行简单查询
        start_time = time.perf_counter()

        with performance_monitor.monitor_operation("test_simple_select"):
            result = self.db_manager.execute_query(
                "SELECT id, name FROM test_customers WHERE id = ?", (1,)
            )

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000  # 转换为毫秒

        # 记录到性能分析器
        self.analyzer.record_query(
            sql="SELECT id, name FROM test_customers WHERE id = ?",
            params=(1,),
            execution_time=execution_time,
            rows_returned=len(result) if result else 0,
        )

        # 验证性能基准
        self.assertLess(
            execution_time,
            self.PERFORMANCE_BENCHMARKS["simple_select"],
            f"简单查询性能不达标: {execution_time:.2f}ms > "
            f"{self.PERFORMANCE_BENCHMARKS['simple_select']}ms",
        )

        # 验证查询结果
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)

        self.logger.info(f"简单查询性能测试通过: {execution_time:.2f}ms")

    def test_complex_join_performance(self):
        """测试复杂连接查询性能"""
        self.logger.info("开始测试复杂连接查询性能")

        # 复杂连接查询SQL
        complex_sql = """
        SELECT c.id, c.name, c.email, i.interaction_type, i.content
        FROM test_customers c
        LEFT JOIN test_interactions i ON c.id = i.customer_id
        WHERE c.created_at >= date('now', '-30 days')
        ORDER BY c.name, i.created_at DESC
        LIMIT 50
        """

        start_time = time.perf_counter()

        with performance_monitor.monitor_operation("test_complex_join"):
            result = self.db_manager.execute_query(complex_sql)

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        # 记录到性能分析器
        self.analyzer.record_query(
            sql=complex_sql,
            execution_time=execution_time,
            rows_returned=len(result) if result else 0,
        )

        # 验证性能基准
        self.assertLess(
            execution_time,
            self.PERFORMANCE_BENCHMARKS["complex_join"],
            f"复杂连接查询性能不达标: {execution_time:.2f}ms > "
            f"{self.PERFORMANCE_BENCHMARKS['complex_join']}ms",
        )

        self.logger.info(f"复杂连接查询性能测试通过: {execution_time:.2f}ms")

    def test_batch_insert_performance(self):
        """测试批量插入性能"""
        self.logger.info("开始测试批量插入性能")

        # 准备批量插入数据
        batch_data = [
            (f"批量客户{i}", f"batch{i}@test.com", f"1380000{i:04d}")
            for i in range(self.TEST_DATA_SIZES["small"])
        ]

        start_time = time.perf_counter()

        with (
            performance_monitor.monitor_operation("test_batch_insert"),
            self.db_manager.transaction() as conn,
        ):
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO test_customers (name, email, phone) VALUES (?, ?, ?)",
                batch_data,
            )
            conn.commit()

        end_time = time.perf_counter()
        execution_time = (end_time - start_time) * 1000

        # 记录到性能分析器
        self.analyzer.record_query(
            sql="INSERT INTO test_customers (name, email, phone) VALUES (?, ?, ?)",
            execution_time=execution_time,
            rows_affected=len(batch_data),
        )

        # 验证性能基准
        self.assertLess(
            execution_time,
            self.PERFORMANCE_BENCHMARKS["insert_batch"],
            f"批量插入性能不达标: {execution_time:.2f}ms > "
            f"{self.PERFORMANCE_BENCHMARKS['insert_batch']}ms",
        )

        # 验证插入结果
        count_result = self.db_manager.execute_query(
            "SELECT COUNT(*) FROM test_customers"
        )
        total_count = count_result[0][0] if count_result else 0
        self.assertGreaterEqual(total_count, len(batch_data))

        self.logger.info(f"批量插入性能测试通过: {execution_time:.2f}ms")

    def test_index_effectiveness(self):
        """测试索引效果"""
        self.logger.info("开始测试索引效果")

        # 测试无索引查询
        no_index_sql = "SELECT * FROM test_customers WHERE email = ?"
        test_email = "test1@example.com"

        start_time = time.perf_counter()
        result_no_index = self.db_manager.execute_query(no_index_sql, (test_email,))
        no_index_time = (time.perf_counter() - start_time) * 1000

        # 创建索引
        self.db_manager.execute_update(
            "CREATE INDEX idx_customer_email ON test_customers(email)"
        )

        # 测试有索引查询
        start_time = time.perf_counter()
        result_with_index = self.db_manager.execute_query(no_index_sql, (test_email,))
        with_index_time = (time.perf_counter() - start_time) * 1000

        # 记录性能数据
        self.analyzer.record_query(
            sql=no_index_sql + " (无索引)",
            params=(test_email,),
            execution_time=no_index_time,
            rows_returned=len(result_no_index) if result_no_index else 0,
        )

        self.analyzer.record_query(
            sql=no_index_sql + " (有索引)",
            params=(test_email,),
            execution_time=with_index_time,
            rows_returned=len(result_with_index) if result_with_index else 0,
        )

        # 验证索引效果（有索引的查询应该更快）
        improvement_ratio = (
            no_index_time / with_index_time if with_index_time > 0 else 1
        )
        self.assertGreater(
            improvement_ratio,
            1.0,
            f"索引未能提升查询性能: 无索引 {no_index_time:.2f}ms, "
            f"有索引 {with_index_time:.2f}ms",
        )

        # 验证查询结果一致性
        self.assertEqual(len(result_no_index), len(result_with_index))

        self.logger.info(
            f"索引效果测试通过: 性能提升 {improvement_ratio:.2f}x "
            f"({no_index_time:.2f}ms -> {with_index_time:.2f}ms)"
        )

    def test_concurrent_query_performance(self):
        """测试并发查询性能"""
        self.logger.info("开始测试并发查询性能")

        import queue
        import threading

        # 并发查询配置
        num_threads = 5
        queries_per_thread = 10
        results_queue = queue.Queue()

        def worker_thread(thread_id: int):
            """工作线程函数"""
            thread_results = []

            for i in range(queries_per_thread):
                start_time = time.perf_counter()

                try:
                    result = self.db_manager.execute_query(
                        "SELECT * FROM test_customers WHERE id = ?",
                        (thread_id * queries_per_thread + i + 1,),
                    )

                    execution_time = (time.perf_counter() - start_time) * 1000

                    thread_results.append(
                        {
                            "thread_id": thread_id,
                            "query_id": i,
                            "execution_time": execution_time,
                            "success": True,
                            "result_count": len(result) if result else 0,
                        }
                    )

                except Exception as e:
                    execution_time = (time.perf_counter() - start_time) * 1000
                    thread_results.append(
                        {
                            "thread_id": thread_id,
                            "query_id": i,
                            "execution_time": execution_time,
                            "success": False,
                            "error": str(e),
                        }
                    )

            results_queue.put(thread_results)

        # 启动并发线程
        threads = []
        overall_start = time.perf_counter()

        for thread_id in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(thread_id,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        overall_time = (time.perf_counter() - overall_start) * 1000

        # 收集结果
        all_results = []
        while not results_queue.empty():
            thread_results = results_queue.get()
            all_results.extend(thread_results)

        # 分析并发性能
        successful_queries = [r for r in all_results if r["success"]]
        [r for r in all_results if not r["success"]]

        if successful_queries:
            avg_query_time = sum(r["execution_time"] for r in successful_queries) / len(
                successful_queries
            )
            max(r["execution_time"] for r in successful_queries)
            min(r["execution_time"] for r in successful_queries)

            # 记录并发性能指标
            self.analyzer.record_query(
                sql="并发查询测试",
                execution_time=avg_query_time,
                rows_returned=len(successful_queries),
            )

            # 验证并发性能
            self.assertLess(
                avg_query_time,
                self.PERFORMANCE_BENCHMARKS["simple_select"] * 2,  # 并发时允许2倍的时间
                f"并发查询平均性能不达标: {avg_query_time:.2f}ms",
            )

            # 验证成功率
            success_rate = len(successful_queries) / len(all_results) * 100
            self.assertGreaterEqual(
                success_rate, 95.0, f"并发查询成功率过低: {success_rate:.1f}%"
            )

            self.logger.info(
                f"并发查询性能测试通过: "
                f"总时间 {overall_time:.2f}ms, "
                f"平均查询时间 {avg_query_time:.2f}ms, "
                f"成功率 {success_rate:.1f}%"
            )

        else:
            self.fail("所有并发查询都失败了")

    def test_slow_query_detection(self):
        """测试慢查询检测"""
        self.logger.info("开始测试慢查询检测")

        # 故意创建慢查询（全表扫描）
        slow_sql = """
        SELECT c1.*, c2.name as related_name
        FROM test_customers c1, test_customers c2
        WHERE c1.name LIKE '%test%' AND c2.name LIKE '%test%'
        LIMIT 10
        """

        start_time = time.perf_counter()
        result = self.db_manager.execute_query(slow_sql)
        execution_time = (time.perf_counter() - start_time) * 1000

        # 记录到性能分析器
        query_id = self.analyzer.record_query(
            sql=slow_sql,
            execution_time=execution_time,
            rows_returned=len(result) if result else 0,
        )

        # 验证慢查询检测
        slow_queries = self.analyzer.get_slow_queries(limit=10)
        slow_query_found = any(q.query_id == query_id for q in slow_queries)

        if execution_time >= self.analyzer._slow_query_threshold:
            self.assertTrue(
                slow_query_found,
                f"慢查询未被正确检测: {execution_time:.2f}ms >= "
                f"{self.analyzer._slow_query_threshold}ms",
            )
            self.logger.info(f"慢查询检测测试通过: {execution_time:.2f}ms")
        else:
            self.logger.info(f"查询执行较快，未触发慢查询检测: {execution_time:.2f}ms")

    def test_database_performance_report(self):
        """测试数据库性能报告生成"""
        self.logger.info("开始测试数据库性能报告生成")

        # 执行一系列查询以生成性能数据
        test_queries = [
            ("SELECT COUNT(*) FROM test_customers", ()),
            ("SELECT * FROM test_customers WHERE id = ?", (1,)),
            ("SELECT * FROM test_customers ORDER BY name LIMIT 10", ()),
            (
                "INSERT INTO test_customers (name, email, phone) VALUES (?, ?, ?)",
                ("报告测试客户", "report@test.com", "13800000000"),
            ),
        ]

        for sql, params in test_queries:
            start_time = time.perf_counter()

            if sql.strip().upper().startswith("SELECT"):
                result = self.db_manager.execute_query(sql, params)
                rows_count = len(result) if result else 0
            else:
                rows_count = self.db_manager.execute_update(sql, params)

            execution_time = (time.perf_counter() - start_time) * 1000

            self.analyzer.record_query(
                sql=sql,
                params=params,
                execution_time=execution_time,
                rows_returned=rows_count
                if sql.strip().upper().startswith("SELECT")
                else 0,
                rows_affected=rows_count
                if not sql.strip().upper().startswith("SELECT")
                else 0,
            )

        # 生成性能报告
        report = self.analyzer.generate_performance_report()

        # 验证报告结构
        self.assertIn("report_timestamp", report)
        self.assertIn("overall_statistics", report)
        self.assertIn("table_statistics", report)
        self.assertIn("operation_statistics", report)
        self.assertIn("connection_statistics", report)
        self.assertIn("recommendations", report)

        # 验证统计数据
        overall_stats = report["overall_statistics"]
        self.assertGreater(overall_stats["total_queries"], 0)
        self.assertGreaterEqual(overall_stats["avg_execution_time_ms"], 0)

        # 验证建议
        recommendations = report["recommendations"]
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

        self.logger.info("数据库性能报告生成测试通过")

    def test_performance_regression_detection(self):
        """测试性能回归检测"""
        self.logger.info("开始测试性能回归检测")

        # 基准性能测试
        baseline_times = []
        test_sql = "SELECT * FROM test_customers WHERE name LIKE ? LIMIT 10"
        test_param = ("test%",)

        # 执行多次查询建立基准
        for _i in range(10):
            start_time = time.perf_counter()
            result = self.db_manager.execute_query(test_sql, test_param)
            execution_time = (time.perf_counter() - start_time) * 1000
            baseline_times.append(execution_time)

            self.analyzer.record_query(
                sql=test_sql,
                params=test_param,
                execution_time=execution_time,
                rows_returned=len(result) if result else 0,
            )

        # 计算基准性能
        baseline_avg = sum(baseline_times) / len(baseline_times)
        max(baseline_times)

        # 模拟性能回归（添加大量数据）
        large_batch_data = [
            (f"回归测试客户{i}", f"regression{i}@test.com", f"1390000{i:04d}")
            for i in range(self.TEST_DATA_SIZES["medium"])
        ]

        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO test_customers (name, email, phone) VALUES (?, ?, ?)",
                large_batch_data,
            )

        # 再次执行相同查询
        regression_times = []
        for _i in range(10):
            start_time = time.perf_counter()
            result = self.db_manager.execute_query(test_sql, test_param)
            execution_time = (time.perf_counter() - start_time) * 1000
            regression_times.append(execution_time)

        regression_avg = sum(regression_times) / len(regression_times)

        # 检测性能回归
        performance_degradation = (regression_avg - baseline_avg) / baseline_avg * 100

        self.logger.info(
            f"性能回归检测: 基准 {baseline_avg:.2f}ms, "
            f"当前 {regression_avg:.2f}ms, "
            f"变化 {performance_degradation:+.1f}%"
        )

        # 如果性能下降超过50%，认为存在回归
        if performance_degradation > 50:
            self.logger.warning(f"检测到性能回归: {performance_degradation:.1f}%")
        else:
            self.logger.info("未检测到显著性能回归")

    def _create_test_tables(self):
        """创建测试表结构"""
        # 客户表
        self.db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS test_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 互动记录表
        self.db_manager.execute_update("""
            CREATE TABLE IF NOT EXISTS test_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                interaction_type TEXT,
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES test_customers (id)
            )
        """)

        self.logger.debug("测试表结构创建完成")

    def _insert_test_data(self):
        """插入测试数据"""
        # 插入客户数据
        customer_data = [
            (f"测试客户{i}", f"test{i}@example.com", f"1380000{i:04d}")
            for i in range(1, self.TEST_DATA_SIZES["small"] + 1)
        ]

        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT INTO test_customers (name, email, phone) VALUES (?, ?, ?)",
                customer_data,
            )

            # 插入互动记录数据
            interaction_data = [
                (i % self.TEST_DATA_SIZES["small"] + 1, "电话", f"与客户{i}的电话沟通")
                for i in range(1, self.TEST_DATA_SIZES["small"] * 2 + 1)
            ]

            cursor.executemany(
                """INSERT INTO test_interactions
                   (customer_id, interaction_type, content) VALUES (?, ?, ?)""",
                interaction_data,
            )

            conn.commit()

        self.logger.debug(
            f"测试数据插入完成: {len(customer_data)}个客户, "
            f"{len(interaction_data)}条互动记录"
        )


class DatabasePerformanceBenchmark(unittest.TestCase):
    """数据库性能基准测试"""

    def setUp(self):
        """基准测试初始化"""
        self.logger = logging.getLogger(__name__)
        self.test_db_path = tempfile.mktemp(suffix=".db")
        self.db_manager = DatabaseManager(self.test_db_path)
        self.analyzer = DatabasePerformanceAnalyzer()

        # 创建大规模测试数据
        self._create_benchmark_tables()
        self._insert_benchmark_data()

    def tearDown(self):
        """基准测试清理"""
        try:
            if self.db_manager:
                self.db_manager.close()
            if self.test_db_path and Path(self.test_db_path).exists():
                Path(self.test_db_path).unlink()
        except Exception as e:
            self.logger.error(f"基准测试清理失败: {e}")

    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        self.logger.info("开始大数据集性能基准测试")

        # 测试大数据集查询
        large_queries = [
            ("SELECT COUNT(*) FROM benchmark_customers", "计数查询"),
            ("SELECT * FROM benchmark_customers ORDER BY name LIMIT 100", "排序查询"),
            (
                """SELECT c.*, COUNT(i.id) as interaction_count
                   FROM benchmark_customers c
                   LEFT JOIN benchmark_interactions i ON c.id = i.customer_id
                   GROUP BY c.id LIMIT 50""",
                "聚合查询",
            ),
        ]

        results = {}
        for sql, description in large_queries:
            start_time = time.perf_counter()
            result = self.db_manager.execute_query(sql)
            execution_time = (time.perf_counter() - start_time) * 1000

            results[description] = {
                "execution_time_ms": execution_time,
                "result_count": len(result) if result else 0,
            }

            self.logger.info(f"{description}: {execution_time:.2f}ms")

        # 输出基准测试结果
        self.logger.info("大数据集性能基准测试完成:")
        for description, metrics in results.items():
            self.logger.info(f"  {description}: {metrics['execution_time_ms']:.2f}ms")

    def _create_benchmark_tables(self):
        """创建基准测试表"""
        self.db_manager.execute_update("""
            CREATE TABLE benchmark_customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.db_manager.execute_update("""
            CREATE TABLE benchmark_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                interaction_type TEXT,
                content TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES benchmark_customers (id)
            )
        """)

        # 创建索引
        self.db_manager.execute_update(
            "CREATE INDEX idx_benchmark_customer_name ON benchmark_customers(name)"
        )
        self.db_manager.execute_update(
            "CREATE INDEX idx_benchmark_customer_city ON benchmark_customers(city)"
        )
        self.db_manager.execute_update(
            """CREATE INDEX idx_benchmark_interaction_customer
               ON benchmark_interactions(customer_id)"""
        )

    def _insert_benchmark_data(self):
        """插入基准测试数据"""
        import random

        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉"]
        interaction_types = ["电话", "邮件", "会议", "拜访", "微信"]

        # 插入大量客户数据
        customer_data = [
            (
                f"基准客户{i}",
                f"benchmark{i}@example.com",
                f"138{random.randint(10000000, 99999999)}",
                f"地址{i}号",
                random.choice(cities),
            )
            for i in range(1, 5001)  # 5000个客户
        ]

        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """INSERT INTO benchmark_customers
                   (name, email, phone, address, city) VALUES (?, ?, ?, ?, ?)""",
                customer_data,
            )

            # 插入互动记录数据
            interaction_data = [
                (
                    random.randint(1, 5000),  # 随机客户ID
                    random.choice(interaction_types),
                    f"基准互动记录{i}的内容",
                )
                for i in range(1, 15001)  # 15000条互动记录
            ]

            cursor.executemany(
                """INSERT INTO benchmark_interactions
                   (customer_id, interaction_type, content) VALUES (?, ?, ?)""",
                interaction_data,
            )

            conn.commit()

        self.logger.info("基准测试数据插入完成: 5000个客户, 15000条互动记录")


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 运行测试
    unittest.main(verbosity=2)
