# coding: utf-8
import unittest
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import oerp_sauce_lib

EXECUTOR_URL = "http://ivkond:b6dac343-b866-4e8e-b301-8d941aeb0534@ondemand.saucelabs.com:80/wd/hub"
LOGIN = "admin"
PASSWORD = "admin"
DATABASE = "tst"
HOST = "http://localhost:8069"


class SeleniumSauceTests(oerp_sauce_lib.SauceLib):
    @classmethod
    def setUpClass(cls):
        cls.login = LOGIN
        cls.password = PASSWORD
        cls.db = DATABASE
        cls.auth_url = "%s/?db=%s" % (HOST, DATABASE)

        caps = webdriver.DesiredCapabilities.CHROME
        caps['platform'] = "Linux"
        caps['version'] = ""

        cls.driver = webdriver.Remote(
            desired_capabilities=caps,
            command_executor=EXECUTOR_URL
        )
        cls.wait = ui.WebDriverWait(cls.driver, 30)

    def test_00_simple_calculation(self):
        driver = self.driver
        wait = self.wait

        print u"Authorize"
        self.auth()

        print u"Go to Production"
        self.go_to_menu(u"Производство", expect_title=u"Производственные заказы")
        print u"Go to Bill of Materials"
        self.go_to_menu(u"Спецификация", expect_title=u"Спецификация")

        print u"Go to parent bill of material"
        self.click_on_tree_line(u"Игровой компьютер")

        print u"Click edit button"
        self.click_edit_button()

        print u"Click on Production notebook tab"
        self.click_on_notebook_tab(u"Производство")

        print u"Click on Manual Average Quantity Checkbox"
        wait.until(lambda drv: drv.find_element_by_name(u"manual_average_qty"))
        box = driver.find_element_by_name(u"manual_average_qty")
        if not box.get_attribute("checked"):
            box.click()

        print u"Set average quantity to 1"
        self.set_field(u"Среднее кол-во", u"1")

        print u"Click save button"
        self.click_save_button()

        print u"Click calculate button"
        self.click_button(u"Расчитать время и себестоимость")

        old_price_text = self.get_field_value(u"Себестоимость")
        old_price = float(old_price_text.replace(",", "."))
        print u"Get old cost price: %s" % old_price

        print u"Click edit button"
        self.click_edit_button()

        print u"Set new average quantity"
        self.set_field(u"Среднее кол-во", u"8000")

        print u"Click save button"
        self.click_save_button()

        print u"Click calculate button"
        self.click_button(u"Расчитать время и себестоимость")

        new_price_text = self.get_field_value(u"Себестоимость")
        new_price = float(new_price_text.replace(",", "."))
        print u"Get new cost price: %s" % new_price

        self.assertNotEqual(old_price, new_price, u"Cost don't changed")

    @classmethod
    def tearDownClass(self):
        print("Link to your job: https://saucelabs.com/jobs/%s" % self.driver.session_id)
        self.driver.quit()

if __name__ == '__main__':
    unittest.main()