/*
* With Wagtail 6 we use Stimulus, via the controller defined in this file.
* With Wagtail <6 we use vanilla JS, which is in wagtaildraftsharing.js
*/

const getJSONConfig = (name) => {
    const config = document.querySelector(`script#${name}`);
    if (!config) {
        throw new Error('wagtail-config script not found');
    }
    return JSON.parse(config.textContent);
}

const generateSharingLink = (button, revisionId, originalButtonText) => {
    const wagtailConfig = getJSONConfig('wagtail-config');
    const wagtaildraftsharingConfig = getJSONConfig('wagtaildraftsharing-config');

    button.disabled = true;
    button.textContent = 'Copying...';

    fetch(wagtaildraftsharingConfig.urls.create, {
        method: 'POST',
        body: `revision=${revisionId}`,
        credentials: 'same-origin',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': wagtailConfig.CSRF_TOKEN,
        },
    }).then(async res => {
        if (res.ok) {
            const data = await res.json();
            const url = window.location.origin + data.url;
            navigator.clipboard.writeText(url).then(() => {
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalButtonText;
                    button.disabled = false;
                }, 3000);
            })
        } else {
            button.textContent = originalButtonText;
            button.disabled = false;
        }
    }).finally(() => {
    });
}

const addCreateSharinkLinkTriggers = () => {
    const links = document.querySelectorAll('[data-wagtaildraftsharing-create]')

    const onClickLink = (e) => {
        e.preventDefault();
        const button = e.target;
        const revisionId = button.dataset.wagtaildraftsharingCreate;
        const originalButtonText = button.textContent;
        generateSharingLink(button, revisionId, originalButtonText)
    }

    links.forEach(link => {
        link.addEventListener('click', onClickLink);
    })
};

const addCopyLinksToClipboardTriggers = () => {
    // For existing links on the Snippet list view for all existing Draftsharing links

    if(window.draftSharing.snippetTriggersAdded){
        // No need to add triggers - already present
        return;
    }

    const links = document.querySelectorAll('[data-wagtaildraftsharing-snippet-url]')

    const onClickLink = (e) => {
        e.preventDefault()
        const link = e.target;
        const url = link.href;

        navigator.clipboard.writeText(url).then(() => {
            // show success message
            link.textContent = 'Copied!'
            // hide message after 5 seconds
            setTimeout(() => {
                link.textContent = 'Copy'
            }, 3000)
        })
    }

    links.forEach(link => {
        link.textContent = 'Copy';
        link.addEventListener('click', onClickLink);
    })
    window.draftSharing['snippetTriggersAdded'] = true;
};

/* window.StimulusModule.Controller comes from Wagtail. Please see
   https://docs.wagtail.org/en/v6.2.2/extending/extending_client_side.html
*/
class DraftsharingController extends window.StimulusModule.Controller {
    static targets = [ "trigger" ];

    initialize(){
        window.draftSharing = window.draftSharing || {};
        // This only hits a selector that's available on the snippet listing
        // of existing DraftsharingLinks
        addCopyLinksToClipboardTriggers();
    }

    generate(event) {
        event.preventDefault();
        generateSharingLink(this.triggerTarget, this.revisionId, this.originalButtonText);
    }


    get originalButtonText(){
        return this.triggerTarget.textContent;
    }

    get revisionId() {
        return this.triggerTarget.dataset.revision
    }

}
window.wagtail.app.register('wagtaildraftsharing', DraftsharingController)
