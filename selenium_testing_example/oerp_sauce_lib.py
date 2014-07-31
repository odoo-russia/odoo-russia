# coding: utf-8
from openerp.tests.common import BaseCase

class SauceLib(BaseCase):
    """You must specify next fields:
    self.driver(Remote driver)
    self.wait(ui.WebDriverWait)
    self.login
    self.password
    self.auth_url
    """
    @classmethod
    def auth(cls):
        cls.driver.get(cls.auth_url)
        cls.wait.until(lambda driver: driver.find_element_by_name('login'))
        login = cls.driver.find_element_by_name('login')
        login.send_keys(cls.login)
        password = cls.driver.find_element_by_name('password')
        password.send_keys(cls.password)
        cls.driver.find_element_by_name('submit').click()
        cls.wait.until(lambda driver: u'Входящие' in driver.title)

    @classmethod
    def go_to_menu(cls, menu, expect_title=None):
        cls.wait.until(lambda drv: drv.find_element_by_link_text(menu))
        cls.driver.find_element_by_link_text(menu).click()
        if expect_title:
            cls.wait.until(lambda drv: expect_title in drv.title)

    @classmethod
    def click_on_tree_line(cls, line, index=0):
        xpath = u"//*[contains(text(), '%s')]" % line
        cls.wait.until(lambda drv: drv.find_elements_by_xpath(xpath))
        table_line = cls.driver.find_elements_by_xpath(xpath)
        assert table_line and table_line[index], u"No elements with line '%s' with index %s" % (line, index)
        table_line[index].click()

    @classmethod
    def click_edit_button(cls):
        cls.wait.until(lambda drv: drv.find_element_by_class_name(u"oe_form_button_edit"))
        edit_button = cls.driver.find_element_by_class_name(u"oe_form_button_edit")
        edit_button.click()
        cls.wait.until(lambda drv: drv.find_element_by_class_name(u"oe_form_button_save"))

    @classmethod
    def click_save_button(cls):
        cls.wait.until(lambda drv: drv.find_element_by_class_name(u"oe_form_button_save"))
        save_button = cls.driver.find_element_by_class_name(u"oe_form_button_save")
        save_button.click()
        cls.wait.until(lambda drv: drv.find_element_by_class_name(u"oe_form_button_edit"))

    @classmethod
    def click_on_notebook_tab(cls, tab_name):
        notebook = cls.driver.find_element_by_class_name(u"oe_notebook")
        prod_button = notebook.find_element_by_link_text(tab_name)
        prod_button.click()

    @classmethod
    def set_field(cls, field_text, value):
        xpath = u"//*[contains(text(), '%s')]/parent::*/following-sibling::*//input" % field_text
        cls.wait.until(lambda drv: drv.find_elements_by_xpath(xpath))
        fields = cls.driver.find_elements_by_xpath(xpath)
        for field in fields:
            if field.is_displayed():
                field.clear()
                field.send_keys(value)

    @classmethod
    def get_field_value(cls, field_text):
        xpath = u"//*[contains(text(), '%s')]/parent::*/following-sibling::*//span[@class='oe_form_char_content']" % field_text
        cls.wait.until(lambda drv: drv.find_elements_by_xpath(xpath))
        price_field = cls.driver.find_element_by_xpath(xpath)
        return price_field.text

    @classmethod
    def click_button(cls, button_text):
        xpath = u"//*[contains(text(), '%s')]/.." % button_text
        cls.wait.until(lambda drv: drv.find_element_by_xpath(xpath))
        button = cls.driver.find_element_by_xpath(xpath)
        button.click()
        # FIXME: Сомнительно, при открытии wizard возможны глюки
        cls.wait.until(lambda drv: not button.get_attribute("disabled"))


