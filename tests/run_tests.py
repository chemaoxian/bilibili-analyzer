#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bilibili-analyzer 测试运行器

使用方法:
    python run_tests.py           # 运行所有单元测试
    python run_tests.py --unit    # 仅运行单元测试（Mock 测试）
    python run_tests.py --live    # 仅运行集成测试（需要真实 API）
    python run_tests.py --cov     # 生成覆盖率报告

依赖:
    pip install coverage
"""

import unittest
import sys
import os
import argparse

# 添加项目路径
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "..", "src")
sys.path.insert(0, SRC_PATH)
sys.path.insert(0, PROJECT_ROOT)


def create_test_suite(unit_only=False, live_only=False):
    """创建测试套件

    Args:
        unit_only: 仅运行单元测试（Mock 测试）
        live_only: 仅运行集成测试（需要真实 API）

    Returns:
        unittest.TestSuite
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 发现所有测试文件
    test_files = [
        "test_analyzer.py",
        "test_subtitle.py",
        "test_clipper.py",
        "test_cli.py",
    ]

    for test_file in test_files:
        test_path = os.path.join(PROJECT_ROOT, test_file)
        if os.path.exists(test_path):
            # 从文件加载测试
            module_name = test_file[:-3]  # 移除 .py
            spec = unittest.TestLoader().loadTestsFromName(test_file[:-3])
            suite.addTests(spec)

    return suite


def run_tests(verbosity=2, unit_only=False, live_only=False):
    """运行测试

    Args:
        verbosity: 输出详细程度 (0-3)
        unit_only: 仅运行单元测试
        live_only: 仅运行集成测试

    Returns:
        bool: 测试是否全部通过
    """
    suite = create_test_suite(unit_only=unit_only, live_only=live_only)

    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        descriptions=True,
        failfast=False
    )

    result = runner.run(suite)

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行测试数：{result.testsRun}")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    print(f"跳过：{len(result.skipped)}")

    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\n出错的测试:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    return result.wasSuccessful()


def run_with_coverage():
    """使用 coverage 运行测试"""
    try:
        import coverage
    except ImportError:
        print("错误：请先安装 coverage: pip install coverage")
        return False

    cov = coverage.Coverage(
        source=["src"],
        omit=[
            "*/tests/*",
            "*/__init__.py",
        ]
    )

    cov.start()
    success = run_tests(verbosity=0)
    cov.stop()

    print("\n" + "=" * 60)
    print("代码覆盖率报告")
    print("=" * 60)
    cov.report(show_missing=True)

    # 生成 HTML 报告
    html_dir = os.path.join(PROJECT_ROOT, "htmlcov")
    cov.html_report(directory=html_dir)
    print(f"\nHTML 报告已生成：{html_dir}/index.html")

    return success


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="bilibili-analyzer 测试运行器")
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=1,
        help="增加详细程度"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="减少输出"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="仅运行单元测试（Mock 测试）"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="仅运行集成测试（需要真实 API 和 Cookie）"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="生成覆盖率报告"
    )

    args = parser.parse_args()

    # 设置详细程度
    if args.quiet:
        verbosity = 0
    else:
        verbosity = args.verbose

    # 运行测试
    if args.coverage:
        success = run_with_coverage()
    else:
        success = run_tests(
            verbosity=verbosity,
            unit_only=args.unit,
            live_only=args.live
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
